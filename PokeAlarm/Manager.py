# Standard Library Imports
import Queue
import json
import logging
import multiprocessing
import os
import re
import sys
import traceback
from datetime import datetime, timedelta

import gevent
# 3rd Party Imports
import gipc

from Alarms import alarm_factory
from Cache import cache_factory
from Filters import load_pokemon_section, load_pokestop_section, load_gym_section, load_egg_section, \
    load_raid_section
from Geofence import load_geofence_file
from Locale import Locale
from LocationServices import LocationService
from Utils import get_cardinal_dir, get_dist_as_str, get_earth_dist, get_path, get_time_as_str, \
    require_and_remove_key, parse_boolean, contains_arg, get_pokemon_cp_range
# Local Imports
from . import config

log = logging.getLogger('Manager')


class Manager(object):
    def __init__(self, name, google_key, locale, units, timezone, time_limit, max_attempts, location, quiet, cache_type,
                 filter_file, geofence_file, alarm_file, debug):
        # Set the name of the Manager
        self.__name = str(name).lower()
        log.info("----------- Manager '{}' is being created.".format(self.__name))
        self.__debug = debug

        # Get the Google Maps API
        self.__google_key = None
        self.__loc_service = None
        if str(google_key).lower() != 'none':
            self.__google_key = google_key
            self.__loc_service = LocationService(google_key, locale, units)
        else:
            log.warning("NO GOOGLE API KEY SET - Reverse Location and Distance Matrix DTS will NOT be detected.")

        self.__locale = Locale(locale)  # Setup the language-specific stuff
        self.__units = units  # type of unit used for distances
        self.__timezone = timezone  # timezone for time calculations
        self.__time_limit = time_limit  # Minimum time remaining for stops and pokemon

        # Set up the Location Specific Stuff
        self.__location = None  # Location should be [lat, lng] (or None for no location)
        if str(location).lower() != 'none':
            self.set_location(location)
        else:
            log.warning("NO LOCATION SET - this may cause issues with distance related DTS.")

        # Quiet mode
        self.__quiet = quiet

        # Create cache
        self.__cache = cache_factory(cache_type, self.__name)

        # Load and Setup the Pokemon Filters
        self.__pokemon_settings, self.__pokestop_settings, self.__gym_settings = {}, {}, {}
        self.__raid_settings, self.__egg_settings = {}, {}
        self.load_filter_file(get_path(filter_file))

        # Create the Geofences to filter with from given file
        self.__geofences = []
        if str(geofence_file).lower() != 'none':
            self.__geofences = load_geofence_file(get_path(geofence_file))
        # Create the alarms to send notifications out with
        self.__alarms = []
        self.load_alarms_file(get_path(alarm_file), int(max_attempts))

        # Initialize the queue and start the process
        self.__queue = multiprocessing.Queue()
        self.__event = multiprocessing.Event()
        self.__process = None

        log.info("----------- Manager '{}' successfully created.".format(self.__name))

    ############################################## CALLED BY MAIN PROCESS ##############################################

    # Update the object into the queue
    def update(self, obj):
        self.__queue.put(obj)

    # Get the name of this Manager
    def get_name(self):
        return self.__name

    # Tell the process to finish up and go home
    def stop(self):
        log.info("Manager {} shutting down... {} items in queue.".format(self.__name, self.__queue.qsize()))
        self.__event.set()

    def join(self):
        self.__process.join(timeout=10)
        if self.__process.is_alive():
            log.warning("Manager {} could not be stopped in time! Forcing process to stop.")
            self.__process.terminate()
        else:
            log.info("Manager {} successfully stopped!".format(self.__name))

    ####################################################################################################################

    ################################################## MANAGER LOADING  ################################################
    # Load in a new filters file
    def load_filter_file(self, file_path):
        try:
            log.info("Loading Filters from file at {}".format(file_path))
            with open(file_path, 'r') as f:
                filters = json.load(f)
            if type(filters) is not dict:
                log.critical("Filters file's must be a JSON object: { \"pokemon\":{...},... }")

            # Load in the Pokemon Section
            self.__pokemon_settings = load_pokemon_section(
                require_and_remove_key('pokemon', filters, "Filters file."))

            # Load in the Pokestop Section
            self.__pokestop_settings = load_pokestop_section(
                require_and_remove_key('pokestops', filters, "Filters file."))

            # Load in the Gym Section
            self.__gym_settings = load_gym_section(
                require_and_remove_key('gyms', filters, "Filters file."))

            # Load in the Egg Section
            self.__egg_settings = load_egg_section(
                require_and_remove_key("eggs", filters, "Filters file."))

            # Load in the Raid Section
            self.__raid_settings = load_raid_section(
                require_and_remove_key('raids', filters, "Filters file."))

            return

        except ValueError as e:
            log.error("Encountered error while loading Filters: {}: {}".format(type(e).__name__, e))
            log.error(
                "PokeAlarm has encountered a 'ValueError' while loading the Filters file. This typically means your " +
                "file isn't in the correct json format. Try loading your file contents into a json validator.")
        except IOError as e:
            log.error("Encountered error while loading Filters: {}: {}".format(type(e).__name__, e))
            log.error("PokeAlarm was unable to find a filters file at {}." +
                      "Please check that this file exists and PA has read permissions.").format(file_path)
        except Exception as e:
            log.error("Encountered error while loading Filters: {}: {}".format(type(e).__name__, e))
        log.debug("Stack trace: \n {}".format(traceback.format_exc()))
        sys.exit(1)

    def load_alarms_file(self, file_path, max_attempts):
        log.info("Loading Alarms from the file at {}".format(file_path))
        try:
            with open(file_path, 'r') as f:
                alarm_settings = json.load(f)
            if type(alarm_settings) is not list:
                log.critical("Alarms file must be a list of Alarms objects - [ {...}, {...}, ... {...} ]")
                sys.exit(1)
            self.__alarms = []
            for alarm in alarm_settings:
                if parse_boolean(require_and_remove_key('active', alarm, "Alarm objects in Alarms file.")) is True:
                    self.set_optional_args(str(alarm))
                    self.__alarms.append(alarm_factory(alarm, max_attempts, self.__google_key))
                else:
                    log.debug("Alarm not activated: " + alarm['type'] + " because value not set to \"True\"")
            log.info("{} active alarms found.".format(len(self.__alarms)))
            return  # all done
        except ValueError as e:
            log.error("Encountered error while loading Alarms file: {}: {}".format(type(e).__name__, e))
            log.error(
                "PokeAlarm has encountered a 'ValueError' while loading the Alarms file. This typically means your " +
                "file isn't in the correct json format. Try loading your file contents into a json validator.")
        except IOError as e:
            log.error("Encountered error while loading Alarms: {}: {}".format(type(e).__name__, e))
            log.error("PokeAlarm was unable to find a filters file at {}." +
                      "Please check that this file exists and PA has read permissions.").format(file_path)
        except Exception as e:
            log.error("Encountered error while loading Alarms: {}: {}".format(type(e).__name__, e))
        log.debug("Stack trace: \n {}".format(traceback.format_exc()))
        sys.exit(1)

    # Check for optional arguments and enable APIs as needed
    def set_optional_args(self, line):
        # Reverse Location
        args = {'street', 'street_num', 'address', 'postal',
                'neighborhood', 'sublocality', 'city', 'county', 'state', 'country'}
        if contains_arg(line, args):
            if self.__loc_service is None:
                log.critical("Reverse location DTS were detected but no API key was provided!")
                log.critical("Please either remove the DTS, add an API key, or disable the alarm and try again.")
                sys.exit(1)
            self.__loc_service.enable_reverse_location()

        # Walking Dist Matrix
        args = {'walk_dist', 'walk_time'}
        if contains_arg(line, args):
            if self.__location is None:
                log.critical("Walking Distance Matrix DTS were detected but no location was set!")
                log.critical("Please either remove the DTS, set a location, or disable the alarm and try again.")
                sys.exit(1)
            if self.__loc_service is None:
                log.critical("Walking Distance Matrix DTS were detected but no API key was provided!")
                log.critical("Please either remove the DTS, add an API key, or disable the alarm and try again.")
                sys.exit(1)
            self.__loc_service.enable_walking_data()

        # Biking Dist Matrix
        args = {'bike_dist', 'bike_time'}
        if contains_arg(line, args):
            if self.__location is None:
                log.critical("Biking Distance Matrix DTS were detected but no location was set!")
                log.critical("Please either remove the DTS, set a location, or disable the alarm and try again.")
                sys.exit(1)
            if self.__loc_service is None:
                log.critical("Biking Distance Matrix DTS were detected but no API key was provided!")
                log.critical("Please either remove the DTS, add an API key, or disable the alarm and try again.")
                sys.exit(1)
            self.__loc_service.enable_biking_data()

        # Driving Dist Matrix
        args = {'drive_dist', 'drive_time'}
        if contains_arg(line, args):
            if self.__location is None:
                log.critical("Driving Distance Matrix DTS were detected but no location was set!")
                log.critical("Please either remove the DTS, set a location, or disable the alarm and try again.")
                sys.exit(1)
            if self.__loc_service is None:
                log.critical("Driving Distance Matrix DTS were detected but no API key was provided!")
                log.critical("Please either remove the DTS, add an API key, or disable the alarm and try again.")
                sys.exit(1)
            self.__loc_service.enable_driving_data()

    ####################################################################################################################

    ################################################## HANDLE EVENTS  ##################################################

    # Start it up
    def start(self):
        self.__process = gipc.start_process(target=self.run, args=(), name=self.__name)

    def setup_in_process(self):
        # Set up signal handlers for graceful exit
        gevent.signal(gevent.signal.SIGINT, self.stop)
        gevent.signal(gevent.signal.SIGTERM, self.stop)

        # Update config
        config['TIMEZONE'] = self.__timezone
        config['API_KEY'] = self.__google_key
        config['UNITS'] = self.__units
        config['DEBUG'] = self.__debug
        config['ROOT_PATH'] = os.path.abspath("{}/..".format(os.path.dirname(__file__)))

        # Hush some new loggers
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)

        if config['DEBUG'] is True:
            logging.getLogger().setLevel(logging.DEBUG)

        # Conect the alarms and send the start up message
        for alarm in self.__alarms:
            alarm.connect()
            alarm.startup_message()

    # Main event handler loop
    def run(self):
        self.setup_in_process()
        last_clean = datetime.utcnow()
        while True:  # Run forever and ever

            # Clean out visited every 5 minutes
            if datetime.utcnow() - last_clean > timedelta(minutes=5):
                log.debug("Cleaning cache...")
                self.__cache.clean_and_save()
                last_clean = datetime.utcnow()

            try:  # Get next object to process
                obj = self.__queue.get(block=True, timeout=5)
            except Queue.Empty:
                # Check if the process should exit process
                if self.__event.is_set():
                    break
                # Explict context yield
                gevent.sleep(0)
                continue

            try:
                kind = obj['type']
                log.debug("Processing object {} with id {}".format(obj['type'], obj['id']))
                if kind == "pokemon":
                    self.process_pokemon(obj)
                elif kind == "pokestop":
                    self.process_pokestop(obj)
                elif kind == "gym":
                    self.process_gym(obj)
                elif kind == 'egg':
                    self.process_egg(obj)
                elif kind == "raid":
                    self.process_raid(obj)
                else:
                    log.error("!!! Manager does not support {} objects!".format(kind))
                log.debug("Finished processing object {} with id {}".format(obj['type'], obj['id']))
            except Exception as e:
                log.error("Encountered error during processing: {}: {}".format(type(e).__name__, e))
                log.debug("Stack trace: \n {}".format(traceback.format_exc()))
            # Explict context yield
            gevent.sleep(0)
        # Save cache and exit
        self.__cache.clean_and_save()
        exit(0)

    # Set the location of the Manager
    def set_location(self, location):
        prog = re.compile("^(-?\d+\.\d+)[,\s]\s*(-?\d+\.\d+?)$")  # RE for Lat,Lng coordinates
        res = prog.match(location)
        if res:  # If location is in a Lat,Lng coordinate
            self.__location = [float(res.group(1)), float(res.group(2))]
        else:
            if self.__loc_service is None:  # Check if key was provided
                log.error("Unable to find location coordinates by name - no Google API key was provided.")
                return None
            self.__location = self.__loc_service.get_location_from_name(location)

        if self.__location is None:
            log.error("Unable to set location - Please check your settings and try again.")
            sys.exit(1)
        else:
            log.info("Location successfully set to '{},{}'.".format(self.__location[0], self.__location[1]))

    # Check if a given pokemon is active on a filter
    def check_pokemon_filter(self, filters, pkmn, dist):
        passed = False

        cp = pkmn['cp']
        level = pkmn['level']
        iv = pkmn['iv']
        def_ = pkmn['def']
        atk = pkmn['atk']
        sta = pkmn['sta']
        size = pkmn['size']
        gender = pkmn['gender']
        form_id = pkmn['form_id']
        name = pkmn['pkmn']
        quick_id = pkmn['quick_id']
        charge_id = pkmn['charge_id']

        for filt_ct in range(len(filters)):
            filt = filters[filt_ct]

            # Check the distance from the set location
            if dist != 'unkn':
                if filt.check_dist(dist) is False:
                    if self.__quiet is False:
                        log.info("{} rejected: distance ({:.2f}) was not in range {:.2f} to {:.2f} (F #{})".format(
                            name, dist, filt.min_dist, filt.max_dist, filt_ct))
                    continue
            else:
                log.debug("Filter dist was not checked because the manager has no location set.")

            # Check the CP of the Pokemon
            if cp != '?':
                if not filt.check_cp(cp):
                    if self.__quiet is False:
                        log.info("{} rejected: CP ({}) not in range {} to {} - (F #{})".format(
                            name, cp, filt.min_cp, filt.max_cp, filt_ct))
                    continue
            else:
                if filt.ignore_missing is True:
                    log.info("{} rejected: CP information was missing - (F #{})".format(name, filt_ct))
                    continue
                log.debug("Pokemon 'cp' was not checked because it was missing.")

            # Check the Level of the Pokemon
            if level != '?':
                if not filt.check_level(level):
                    if self.__quiet is False:
                        log.info("{} rejected: Level ({}) not in range {} to {} - (F #{})".format(
                            name, level, filt.min_level, filt.max_level, filt_ct))
                    continue
            else:
                if filt.ignore_missing is True:
                    log.info("{} rejected: Level information was missing - (F #{})".format(name, filt_ct))
                    continue
                log.debug("Pokemon 'level' was not checked because it was missing.")

            # Check the IV percent of the Pokemon
            if iv != '?':
                if not filt.check_iv(iv):
                    if self.__quiet is False:
                        log.info("{} rejected: IV percent ({:.2f}) not in range {:.2f} to {:.2f} - (F #{})".format(
                            name, iv, filt.min_iv, filt.max_iv, filt_ct))
                    continue
            else:
                if filt.ignore_missing is True:
                    log.info("{} rejected: 'IV' information was missing (F #{})".format(name, filt_ct))
                    continue
                log.debug("Pokemon IV percent was not checked because it was missing.")

            # Check the Attack IV of the Pokemon
            if atk != '?':
                if not filt.check_atk(atk):
                    if self.__quiet is False:
                        log.info("{} rejected: Attack IV ({}) not in range {} to {} - (F #{})".format(
                            name, atk, filt.min_atk, filt.max_atk, filt_ct))
                    continue
            else:
                if filt.ignore_missing is True:
                    log.info("{} rejected: Attack IV information was missing - (F #{})".format(name, filt_ct))
                    continue
                log.debug("Pokemon 'atk' was not checked because it was missing.")

            # Check the Defense IV of the Pokemon
            if def_ != '?':
                if not filt.check_def(def_):
                    if self.__quiet is False:
                        log.info("{} rejected: Defense IV ({}) not in range {} to {} - (F #{})".format(
                            name, def_, filt.min_atk, filt.max_atk, filt_ct))
                    continue
            else:
                if filt.ignore_missing is True:
                    log.info("{} rejected: Defense IV information was missing - (F #{})".format(name, filt_ct))
                    continue
                log.debug("Pokemon 'def' was not checked because it was missing.")

            # Check the Stamina IV of the Pokemon
            if sta != '?':
                if not filt.check_sta(sta):
                    if self.__quiet is False:
                        log.info("{} rejected: Stamina IV ({}) not in range {} to {} - (F #{}).".format(
                            name, sta, filt.min_sta, filt.max_sta, filt_ct))
                    continue
            else:
                if filt.ignore_missing is True:
                    log.info("{} rejected: Stamina IV information was missing - (F #{})".format(name, filt_ct))
                    continue
                log.debug("Pokemon 'sta' was not checked because it was missing.")

            # Check the Quick Move of the Pokemon
            if quick_id != '?':
                if not filt.check_quick_move(quick_id):
                    if self.__quiet is False:
                        log.info("{} rejected: Quick move was not correct - (F #{})".format(name, filt_ct))
                    continue
            else:
                if filt.ignore_missing is True:
                    log.info("{} rejected: Quick move information was missing - (F #{})".format(name, filt_ct))
                    continue
                log.debug("Pokemon 'quick_id' was not checked because it was missing.")

            # Check the Quick Move of the Pokemon
            if charge_id != '?':
                if not filt.check_charge_move(charge_id):
                    if self.__quiet is False:
                        log.info("{} rejected: Charge move was not correct - (F #{})".format(name, filt_ct))
                    continue
            else:
                if filt.ignore_missing is True:
                    log.info("{} rejected: Charge move information was missing - (F #{})".format(name, filt_ct))
                    continue
                log.debug("Pokemon 'charge_id' was not checked because it was missing.")

            # Check for a correct move combo
            if quick_id != '?' and charge_id != '?':
                if not filt.check_moveset(quick_id, charge_id):
                    if self.__quiet is False:
                        log.info("{} rejected: Moveset was not correct - (F #{})".format(name, filt_ct))
                    continue
            else:  # This will probably never happen? but just to be safe...
                if filt.ignore_missing is True:
                    log.info("{} rejected: Moveset information was missing - (F #{})".format(name, filt_ct))
                    continue
                log.debug("Pokemon 'moveset' was not checked because it was missing.")

            # Check for a valid size
            if size != 'unknown':
                if not filt.check_size(size):
                    if self.__quiet is False:
                        log.info("{} rejected: Size ({}) was not correct - (F #{})".format(name, size, filt_ct))
                    continue
            else:
                if filt.ignore_missing is True:
                    log.info("{} rejected: Size information was missing - (F #{})".format(name, filt_ct))
                    continue
                log.debug("Pokemon 'size' was not checked because it was missing.")

            # Check for a valid gender
            if gender != 'unknown':
                if not filt.check_gender(gender):
                    if self.__quiet is False:
                        log.info("{} rejected: Gender ({}) was not correct - (F #{})".format(name, gender, filt_ct))
                    continue
            else:
                if filt.ignore_missing is True:
                    log.info("{} rejected: Gender information was missing - (F #{})".format(name, filt_ct))
                    continue
                log.debug("Pokemon 'gender' was not checked because it was missing.")

            # Check for a valid form
            if form_id != '?':
                if not filt.check_form(form_id):
                    if self.__quiet is False:
                        log.info("{} rejected: Form ({}) was not correct - (F #{})".format(name, form_id, filt_ct))
                    continue

            # Nothing left to check, so it must have passed
            passed = True
            log.debug("{} passed filter #{}".format(name, filt_ct))
            break

        return passed

    # Check if a raid filter will pass for given raid
    def check_egg_filter(self, settings, egg):
        level = egg['raid_level']

        if level < settings['min_level']:
            if self.__quiet is False:
                log.info("Egg {} is less ({}) than min ({}) level, ignore"
                         .format(egg['id'], level, settings['min_level']))
            return False

        if level > settings['max_level']:
            if self.__quiet is False:
                log.info("Egg {} is higher ({}) than max ({}) level, ignore"
                         .format(egg['id'], level, settings['max_level']))
            return False

        return True

    # Process new Pokemon data and decide if a notification needs to be sent
    def process_pokemon(self, pkmn):
        # Make sure that pokemon are enabled
        if self.__pokemon_settings['enabled'] is False:
            log.debug("Pokemon ignored: pokemon notifications are disabled.")
            return

        # Extract some base information
        pkmn_hash = pkmn['id']
        pkmn_id = pkmn['pkmn_id']
        name = self.__locale.get_pokemon_name(pkmn_id)

        # Check for previously processed
        if self.__cache.get_pokemon_expiration(pkmn_hash) is not None:
            log.debug("{} was skipped because it was previously processed.".format(name))
            return
        self.__cache.update_pokemon_expiration(pkmn_hash, pkmn['disappear_time'])

        # Check the time remaining
        seconds_left = (pkmn['disappear_time'] - datetime.utcnow()).total_seconds()
        if seconds_left < self.__time_limit:
            if self.__quiet is False:
                log.info("{} ignored: Only {} seconds remaining.".format(name, seconds_left))
            return

        # Check that the filter is even set
        if pkmn_id not in self.__pokemon_settings['filters']:
            if self.__quiet is False:
                log.info("{} ignored: no filters are set".format(name))
            return

        # Extract some useful info that will be used in the filters

        lat, lng = pkmn['lat'], pkmn['lng']
        dist = get_earth_dist([lat, lng], self.__location)

        pkmn['pkmn'] = name

        filters = self.__pokemon_settings['filters'][pkmn_id]
        passed = self.check_pokemon_filter(filters, pkmn, dist)
        # If we didn't pass any filters
        if not passed:
            return

        quick_id = pkmn['quick_id']
        charge_id = pkmn['charge_id']

        # Check all the geofences
        pkmn['geofence'] = self.check_geofences(name, lat, lng)
        if len(self.__geofences) > 0 and pkmn['geofence'] == 'unknown':
            log.info("{} rejected: not inside geofence(s)".format(name))
            return

        # Finally, add in all the extra crap we waited to calculate until now
        time_str = get_time_as_str(pkmn['disappear_time'], self.__timezone)
        iv = pkmn['iv']
        form_id = pkmn['form_id']
        form = self.__locale.get_form_name(pkmn_id, form_id)

        pkmn.update({
            'pkmn': name,
            'pkmn_id_3': '{:03}'.format(pkmn_id),
            "dist": get_dist_as_str(dist) if dist != 'unkn' else 'unkn',
            'time_left': time_str[0],
            '12h_time': time_str[1],
            '24h_time': time_str[2],
            'dir': get_cardinal_dir([lat, lng], self.__location),
            'iv_0': "{:.0f}".format(iv) if iv != '?' else '?',
            'iv': "{:.1f}".format(iv) if iv != '?' else '?',
            'iv_2': "{:.2f}".format(iv) if iv != '?' else '?',
            'quick_move': self.__locale.get_move_name(quick_id),
            'charge_move': self.__locale.get_move_name(charge_id),
            'form_id_or_empty': '' if form_id == '?' else '{:03}'.format(form_id),
            'form': form,
            'form_or_empty': '' if form == 'unknown' else form
        })
        if self.__loc_service:
            self.__loc_service.add_optional_arguments(self.__location, [lat, lng], pkmn)

        if self.__quiet is False:
            log.info("{} notification has been triggered!".format(name))

        threads = []
        # Spawn notifications in threads so they can work in background
        for alarm in self.__alarms:
            threads.append(gevent.spawn(alarm.pokemon_alert, pkmn))
            gevent.sleep(0)  # explict context yield

        for thread in threads:
            thread.join()

    def process_pokestop(self, stop):
        # Make sure that pokemon are enabled
        if self.__pokestop_settings['enabled'] is False:
            log.debug("Pokestop ignored: pokestop notifications are disabled.")
            return

        stop_id = stop['id']

        # Check for previously processed
        if self.__cache.get_pokestop_expiration(stop_id) is not None:
            log.debug("Pokestop was skipped because it was previously processed.")
            return
        self.__cache.update_pokestop_expiration(stop_id, stop['expire_time'])

        # Check the time remaining
        seconds_left = (stop['expire_time'] - datetime.utcnow()).total_seconds()
        if seconds_left < self.__time_limit:
            if self.__quiet is False:
                log.info("Pokestop ({}) ignored: only {} seconds remaining.".format(stop_id, seconds_left))
            return

        # Extract some basic information
        lat, lng = stop['lat'], stop['lng']
        dist = get_earth_dist([lat, lng], self.__location)
        passed = False
        filters = self.__pokestop_settings['filters']
        for filt_ct in range(len(filters)):
            filt = filters[filt_ct]
            # Check the distance from the set location
            if dist != 'unkn':
                if filt.check_dist(dist) is False:
                    if self.__quiet is False:
                        log.info("Pokestop rejected: distance ({:.2f}) was not in range".format(dist) +
                                 " {:.2f} to {:.2f} (F #{})".format(filt.min_dist, filt.max_dist, filt_ct))
                    continue
            else:
                log.debug("Pokestop dist was not checked because the manager has no location set.")

            # Nothing left to check, so it must have passed
            passed = True
            log.debug("Pokstop passed filter #{}".format(filt_ct))
            break

        if not passed:
            return

        # Check the geofences
        stop['geofence'] = self.check_geofences('Pokestop', lat, lng)
        if len(self.__geofences) > 0 and stop['geofence'] == 'unknown':
            log.info("Pokestop rejected: not within any specified geofence")
            return

        time_str = get_time_as_str(stop['expire_time'], self.__timezone)
        stop.update({
            "dist": get_dist_as_str(dist),
            'time_left': time_str[0],
            '12h_time': time_str[1],
            '24h_time': time_str[2],
            'dir': get_cardinal_dir([lat, lng], self.__location),
        })
        if self.__loc_service:
            self.__loc_service.add_optional_arguments(self.__location, [lat, lng], stop)

        if self.__quiet is False:
            log.info("Pokestop ({}) notification has been triggered!".format(stop_id))

        threads = []
        # Spawn notifications in threads so they can work in background
        for alarm in self.__alarms:
            threads.append(gevent.spawn(alarm.pokestop_alert, stop))
            gevent.sleep(0)  # explict context yield

        for thread in threads:
            thread.join()

    def process_gym(self, gym):
        gym_id = gym['id']

        # Update Gym details (if they exist)
        self.__cache.update_gym_info(gym_id, gym['name'], gym['description'], gym['url'])

        # Extract some basic information
        to_team_id = gym['new_team_id']
        from_team_id = self.__cache.get_gym_team(gym_id)

        # Ignore changes to neutral
        if self.__gym_settings['ignore_neutral'] and to_team_id == 0:
            log.debug("Gym update ignored: changed to neutral")
            return

        # Update gym's last known team
        self.__cache.update_gym_team(gym_id, to_team_id)

        # Check if notifications are on
        if self.__gym_settings['enabled'] is False:
            log.debug("Gym ignored: notifications are disabled.")
            return

        # Doesn't look like anything to me
        if to_team_id == from_team_id:
            log.debug("Gym ignored: no change detected")
            return

        # Ignore first time updates
        if from_team_id is '?':
            log.debug("Gym update ignored: first time seeing this gym")
            return

        # Get some more info out used to check filters
        lat, lng = gym['lat'], gym['lng']
        dist = get_earth_dist([lat, lng], self.__location)
        cur_team = self.__locale.get_team_name(to_team_id)
        old_team = self.__locale.get_team_name(from_team_id)

        filters = self.__gym_settings['filters']
        passed = False
        for filt_ct in range(len(filters)):
            filt = filters[filt_ct]
            # Check the distance from the set location
            if dist != 'unkn':
                if filt.check_dist(dist) is False:
                    if self.__quiet is False:
                        log.info("Gym rejected: distance ({:.2f}) was not in range" +
                                 " {:.2f} to {:.2f} (F #{})".format(dist, filt.min_dist, filt.max_dist, filt_ct))
                    continue
            else:
                log.debug("Gym dist was not checked because the manager has no location set.")

            # Check the old team
            if filt.check_from_team(from_team_id) is False:
                if self.__quiet is False:
                    log.info("Gym rejected: {} as old team is not correct (F #{})".format(old_team, filt_ct))
                continue
            # Check the new team
            if filt.check_to_team(to_team_id) is False:
                if self.__quiet is False:
                    log.info("Gym rejected: {} as current team is not correct (F #{})".format(cur_team, filt_ct))
                continue

            # Nothing left to check, so it must have passed
            passed = True
            log.debug("Gym passed filter #{}".format(filt_ct))
            break

        if not passed:
            return

        # Check the geofences
        gym['geofence'] = self.check_geofences('Gym', lat, lng)
        if len(self.__geofences) > 0 and gym['geofence'] == 'unknown':
            log.info("Gym rejected: not inside geofence(s)")
            return

        # Check if in geofences
        if len(self.__geofences) > 0:
            inside = False
            for gf in self.__geofences:
                inside |= gf.contains(lat, lng)
            if inside is False:
                if self.__quiet is False:
                    log.info("Gym update ignored: located outside geofences.")
                return
        else:
            log.debug("Gym inside geofences was not checked because no geofences were set.")

        gym_info = self.__cache.get_gym_info(gym_id)

        gym.update({
            "gym_name": gym_info['name'],
            "gym_description": gym_info['description'],
            "gym_url": gym_info['url'],
            "dist": get_dist_as_str(dist),
            'dir': get_cardinal_dir([lat, lng], self.__location),
            'new_team': cur_team,
            'new_team_id': to_team_id,
            'old_team': old_team,
            'old_team_id': from_team_id,
            'new_team_leader': self.__locale.get_leader_name(to_team_id),
            'old_team_leader': self.__locale.get_leader_name(from_team_id)
        })
        if self.__loc_service:
            self.__loc_service.add_optional_arguments(self.__location, [lat, lng], gym)

        if self.__quiet is False:
            log.info("Gym ({}) notification has been triggered!".format(gym_id))

        threads = []
        # Spawn notifications in threads so they can work in background
        for alarm in self.__alarms:
            threads.append(gevent.spawn(alarm.gym_alert, gym))
            gevent.sleep(0)  # explict context yield

        for thread in threads:
            thread.join()

    def process_egg(self, egg):
        # Quick check for enabled
        if self.__egg_settings['enabled'] is False:
            log.debug("Egg ignored: notifications are disabled.")
            return

        gym_id = egg['id']

        # Check if egg has been processed yet
        if self.__cache.get_egg_expiration(gym_id) is not None:
            if self.__quiet is False:
                log.info("Egg {} ignored - previously processed.".format(gym_id))
            return

        # Update egg hatch
        self.__cache.update_egg_expiration(gym_id, egg['raid_begin'])

        # don't alert about (nearly) hatched eggs
        seconds_left = (egg['raid_begin'] - datetime.utcnow()).total_seconds()
        if seconds_left < self.__time_limit:
            if self.__quiet is False:
                log.info("Egg {} ignored. Egg hatch in {} seconds".format(gym_id, seconds_left))
            return

        lat, lng = egg['lat'], egg['lng']
        dist = get_earth_dist([lat, lng], self.__location)

        # Check if raid is in geofences
        egg['geofence'] = self.check_geofences('Raid', lat, lng)
        if len(self.__geofences) > 0 and egg['geofence'] == 'unknown':
            if self.__quiet is False:
                log.info("Egg {} ignored: located outside geofences.".format(gym_id))
            return
        else:
            log.debug("Egg inside geofence was not checked because no geofences were set.")

        # check if the level is in the filter range or if we are ignoring eggs
        passed = self.check_egg_filter(self.__egg_settings, egg)

        if not passed:
            log.debug("Egg {} did not pass filter check".format(gym_id))
            return

        if self.__loc_service:
            self.__loc_service.add_optional_arguments(self.__location, [lat, lng], egg)

        if self.__quiet is False:
            log.info("Egg ({}) notification has been triggered!".format(gym_id))

        time_str = get_time_as_str(egg['raid_end'], self.__timezone)
        start_time_str = get_time_as_str(egg['raid_begin'], self.__timezone)

        # team id saved in self.__gym_hist when processing gym
        team_id = self.__cache.get_gym_team(gym_id)
        gym_info = self.__cache.get_gym_info(gym_id)

        if egg['gym_name'] == 'unknown':  # if RM or empty
            egg.update({"gym_name": gym_info['name']})

        egg.update({
            "gym_description": gym_info['description'],
            "gym_url": gym_info['url'],
            'time_left': time_str[0],
            '12h_time': time_str[1],
            '24h_time': time_str[2],
            'begin_time_left': start_time_str[0],
            'begin_12h_time': start_time_str[1],
            'begin_24h_time': start_time_str[2],
            "dist": get_dist_as_str(dist),
            'dir': get_cardinal_dir([lat, lng], self.__location),
            'team_id': team_id,
            'team_name': self.__locale.get_team_name(team_id)
        })

        threads = []
        # Spawn notifications in threads so they can work in background
        for alarm in self.__alarms:
            threads.append(gevent.spawn(alarm.raid_egg_alert, egg))
            gevent.sleep(0)  # explict context yield

        for thread in threads:
            thread.join()

    def process_raid(self, raid):
        # Quick check for enabled
        if self.__raid_settings['enabled'] is False:
            log.debug("Raid ignored: notifications are disabled.")
            return

        gym_id = raid['id']

        pkmn_id = raid['pkmn_id']
        raid_end = raid['raid_end']

        # Check if raid has been processed
        if self.__cache.get_raid_expiration(gym_id) is not None:
            if self.__quiet is False:
                log.info("Raid {} ignored. Was previously processed.".format(gym_id))
            return

        self.__cache.update_raid_expiration(gym_id, raid_end)
        log.info(self.__cache.get_raid_expiration(gym_id))
        # don't alert about expired raids
        seconds_left = (raid_end - datetime.utcnow()).total_seconds()
        if seconds_left < self.__time_limit:
            if self.__quiet is False:
                log.info("Raid {} ignored. Only {} seconds left.".format(gym_id, seconds_left))
            return

        lat, lng = raid['lat'], raid['lng']
        dist = get_earth_dist([lat, lng], self.__location)

        # Check if raid is in geofences
        raid['geofence'] = self.check_geofences('Raid', lat, lng)
        if len(self.__geofences) > 0 and raid['geofence'] == 'unknown':
            if self.__quiet is False:
                log.info("Raid {} ignored: located outside geofences.".format(gym_id))
            return
        else:
            log.debug("Raid inside geofence was not checked because no geofences were set.")

        quick_id = raid['quick_id']
        charge_id = raid['charge_id']

        #  check filters for pokemon
        name = self.__locale.get_pokemon_name(pkmn_id)

        if pkmn_id not in self.__raid_settings['filters']:
            if self.__quiet is False:
                log.info("Raid on {} ignored: no filters are set".format(name))
            return

        # TODO: Raid filters - don't need all of these attributes/checks
        raid_pkmn = {
            'pkmn': name,
            'cp': raid['cp'],
            'iv': 100,
            'level': 20,
            'def': 15,
            'atk': 15,
            'sta': 15,
            'gender': 'unknown',
            'size': 'unknown',
            'form_id': '?',
            'quick_id': quick_id,
            'charge_id': charge_id
        }

        filters = self.__raid_settings['filters'][pkmn_id]
        passed = self.check_pokemon_filter(filters, raid_pkmn, dist)
        # If we didn't pass any filters
        if not passed:
            log.debug("Raid {} did not pass pokemon check".format(gym_id))
            return

        if self.__loc_service:
            self.__loc_service.add_optional_arguments(self.__location, [lat, lng], raid)

        if self.__quiet is False:
            log.info("Raid ({}) notification has been triggered!".format(gym_id))

        time_str = get_time_as_str(raid['raid_end'], self.__timezone)
        start_time_str = get_time_as_str(raid['raid_begin'], self.__timezone)

        # team id saved in self.__gym_hist when processing gym
        team_id = self.__cache.get_gym_team(gym_id)
        gym_info = self.__cache.get_gym_info(gym_id)
        form_id = raid_pkmn['form_id']
        form = self.__locale.get_form_name(pkmn_id, form_id)
        min_cp, max_cp = get_pokemon_cp_range(pkmn_id, 20)

	if raid['gym_name'] == 'unknown':  # if RM or empty
	    raid.update({"gym_name": gym_info['name']})
        
        raid.update({
            'pkmn': name,
            'pkmn_id_3': '{:03}'.format(pkmn_id),
            "gym_name": gym_info['name'],
            "gym_description": gym_info['description'],
            "gym_url": gym_info['url'],
            'time_left': time_str[0],
            '12h_time': time_str[1],
            '24h_time': time_str[2],
            'begin_time_left': start_time_str[0],
            'begin_12h_time': start_time_str[1],
            'begin_24h_time': start_time_str[2],
            "dist": get_dist_as_str(dist),
            'dir': get_cardinal_dir([lat, lng], self.__location),
            'quick_move': self.__locale.get_move_name(quick_id),
            'charge_move': self.__locale.get_move_name(charge_id),
            'form_id_or_empty': '' if form_id == '?' else '{:03}'.format(form_id),
            'form': form,
            'form_or_empty': '' if form == 'unknown' else form,
            'team_id': team_id,
            'team_name': self.__locale.get_team_name(team_id),
            'min_cp': min_cp,
            'max_cp': max_cp
        })

        threads = []
        # Spawn notifications in threads so they can work in background
        for alarm in self.__alarms:
            threads.append(gevent.spawn(alarm.raid_alert, raid))

            gevent.sleep(0)  # explict context yield

        for thread in threads:
            thread.join()

    # Check to see if a notification is within the given range
    def check_geofences(self, name, lat, lng):
        for gf in self.__geofences:
            if gf.contains(lat, lng):
                log.debug("{} is in geofence {}!".format(name, gf.get_name()))
                return gf.get_name()
            else:
                log.debug("{} is not in geofence {}".format(name, gf.get_name()))
        return 'unknown'

    ####################################################################################################################

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

# Local Imports
import Alarms
import Filters
import Events
from Cache import cache_factory
from Geofence import load_geofence_file
from Locale import Locale
from LocationServices import location_service_factory
from Utils import get_cardinal_dir, get_dist_as_str, get_earth_dist, get_path,\
    get_time_as_str, require_and_remove_key, parse_boolean, contains_arg, \
    get_pokemon_cp_range
from . import config

log = logging.getLogger('Manager')


class Manager(object):
    def __init__(self, name, google_key, locale, units, timezone, time_limit,
                 max_attempts, location, quiet, cache_type, filter_file,
                 geofence_file, alarm_file, debug):
        # Set the name of the Manager
        self.__name = str(name).lower()
        log.info("----------- Manager '{}' ".format(self.__name)
                 + " is being created.")
        self.__debug = debug

        # Get the Google Maps API
        self.__google_key = None
        self.__loc_service = None
        if str(google_key).lower() != 'none':
            self.__google_key = google_key
            self.__loc_service = location_service_factory(
                "GoogleMaps", google_key, locale, units)
        else:
            log.warning("NO GOOGLE API KEY SET - Reverse Location and"
                        + " Distance Matrix DTS will NOT be detected.")

        self.__locale = Locale(locale)  # Setup the language-specific stuff
        self.__units = units  # type of unit used for distances
        self.__timezone = timezone  # timezone for time calculations
        self.__time_limit = time_limit  # Minimum time remaining

        # Location should be [lat, lng] (or None for no location)
        self.__location = None
        if str(location).lower() != 'none':
            self.set_location(location)
        else:
            log.warning("NO LOCATION SET - "
                        + " this may cause issues with distance related DTS.")

        # Quiet mode
        self.__quiet = quiet

        # Create cache
        self.__cache = cache_factory(cache_type, self.__name)

        # Load and Setup the Pokemon Filters
        self.__mons_enabled, self.__mon_filters = True, {}
        self.__stops_enabled, self.__stop_filters = True, {}
        self.__gyms_enabled, self.__gym_filters = True, {}
        self.__ignore_neutral = False
        self.__eggs_enabled, self.__egg_filters = False, {}
        self.__raids_enabled, self.__raid_filters = False, {}
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

        log.info("----------- Manager '{}' ".format(self.__name)
                 + " successfully created.")

    # ~~~~~~~~~~~~~~~~~~~~~~~ MAIN PROCESS CONTROL ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # Update the object into the queue
    def update(self, obj):
        self.__queue.put(obj)

    # Get the name of this Manager
    def get_name(self):
        return self.__name

    # Tell the process to finish up and go home
    def stop(self):
        log.info("Manager {} shutting down... ".format(self.__name)
                 + "{} items in queue.".format(self.__queue.qsize()))
        self.__event.set()

    def join(self):
        self.__process.join(timeout=10)
        if self.__process.is_alive():
            log.warning("Manager {} could not be stopped in time!"
                        + " Forcing process to stop.")
            self.__process.terminate()
        else:
            log.info("Manager {} successfully stopped!".format(self.__name))

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ MANAGER LOADING ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @staticmethod
    def load_filter_section(section, sect_name, filter_type):
        defaults = section.pop('defaults', {})
        filter_set = {}
        for name, settings in section.pop('filters', {}).iteritems():
            settings = dict(settings.items() + defaults.items())
            filter_set[name] = filter_type(name, settings)
            log.debug(
                "Filter '%s' set as the following: %s", name,
                filter_set[name].to_dict())
        for key in section:  # Reject leftover parameters
            raise ValueError("'{}' is not a recognized parameter for the"
                             " '{}' section.".format(key, sect_name))
        return filter_set

    # Load in a new filters file
    def load_filter_file(self, file_path):
        try:
            log.info("Loading Filters from file at {}".format(file_path))
            with open(file_path, 'r') as f:
                filters = json.load(f)
            if type(filters) is not dict:
                log.critical("Filters file's must be a JSON object:"
                             + " { \"monsters\":{...},... }")
        except ValueError as e:
            log.error("Encountered error while loading Filters:"
                      + " {}: {}".format(type(e).__name__, e))
            log.error(
                "PokeAlarm has encountered a 'ValueError' while loading the"
                + " Filters file. This typically means your file isn't in the"
                + "correct json format. Try loading your file contents into a"
                + " json validator.")
            log.debug("Stack trace: \n {}".format(traceback.format_exc()))
            sys.exit(1)
        except IOError as e:
            log.error("Encountered error while loading Filters: "
                      + "{}: {}".format(type(e).__name__, e))
            log.error("PokeAlarm was unable to find a filters file"
                      + " at {}. Please check that this ".format(file_path)
                      + " file exists and that PA has read permissions.")
            log.debug("Stack trace: \n {}".format(traceback.format_exc()))
            sys.exit(1)

        try:
            # Load Monsters Section
            section = filters.pop('monsters', {})
            self.__mons_enabled = bool(section.pop('enabled', True))
            self.__mon_filters = self.load_filter_section(
                section, 'monsters', Filters.MonFilter)

            # Load Stops Section
            section = filters.pop('stops', {})
            self.__stops_enabled = bool(section.pop('enabled', True))
            self.__stop_filters = self.load_filter_section(
                section, 'stops', Filters.StopFilter)

            # Load Gyms Section
            section = filters.pop('gyms', {})
            self.__gyms_enabled = bool(section.pop('enabled', True))
            self.__ignore_neutral = bool(section.pop('ignore_neutral', False))
            self.__gym_filters = self.load_filter_section(
                section, 'gyms', Filters.GymFilter)

            # Load Eggs Section
            section = filters.pop('eggs', {})
            self.__eggs_enabled = bool(section.pop('enabled', True))
            self.__egg_filters = self.load_filter_section(
                section, 'eggs', Filters.EggFilter)

            # Load Raids Section
            section = filters.pop('raids', {})
            self.__raids_enabled = bool(section.pop('enabled', True))
            self.__raid_filters = self.load_filter_section(
                section, 'raids', Filters.RaidFilter)

            return  # exit function

        except Exception as e:
            log.error("Encountered error while parsing Filters. "
                      "This is because of a mistake in your Filters file.")
            log.error("{}: {}".format(type(e).__name__, e))
            log.debug("Stack trace: \n {}".format(traceback.format_exc()))
            sys.exit(1)

    def load_alarms_file(self, file_path, max_attempts):
        log.info("Loading Alarms from the file at {}".format(file_path))
        try:
            with open(file_path, 'r') as f:
                alarm_settings = json.load(f)
            if type(alarm_settings) is not list:
                log.critical("Alarms file must be a list of Alarms objects "
                             + "- [ {...}, {...}, ... {...} ]")
                sys.exit(1)
            self.__alarms = []
            for alarm in alarm_settings:
                if parse_boolean(require_and_remove_key(
                        'active', alarm, "Alarm objects in file.")) is True:
                    self.set_optional_args(str(alarm))
                    self.__alarms.append(Alarms.alarm_factory(
                            alarm, max_attempts, self.__google_key))
                else:
                    log.debug("Alarm not activated: {}".format(alarm['type'])
                              + " because value not set to \"True\"")
            log.info("{} active alarms found.".format(len(self.__alarms)))
            return  # all done
        except ValueError as e:
            log.error("Encountered error while loading Alarms file: "
                      + "{}: {}".format(type(e).__name__, e))
            log.error(
                "PokeAlarm has encountered a 'ValueError' while loading the "
                + " Alarms file. This typically means your file isn't in the "
                + "correct json format. Try loading your file contents into"
                + " a json validator.")
        except IOError as e:
            log.error("Encountered error while loading Alarms: "
                      + "{}: {}".format(type(e).__name__, e))
            log.error("PokeAlarm was unable to find a filters file "
                      + "at {}. Please check that this file".format(file_path)
                      + " exists and PA has read permissions.")
        except Exception as e:
            log.error("Encountered error while loading Alarms: "
                      + "{}: {}".format(type(e).__name__, e))
        log.debug("Stack trace: \n {}".format(traceback.format_exc()))
        sys.exit(1)

    # Check for optional arguments and enable APIs as needed
    def set_optional_args(self, line):
        # Reverse Location
        args = {'street', 'street_num', 'address', 'postal', 'neighborhood',
                'sublocality', 'city', 'county', 'state', 'country'}
        if contains_arg(line, args):
            if self.__loc_service is None:
                log.critical("Reverse location DTS were detected but "
                             + "no API key was provided!")
                log.critical("Please either remove the DTS, add an API key, "
                             + "or disable the alarm and try again.")
                sys.exit(1)
            self.__loc_service.enable_reverse_location()

        # Walking Dist Matrix
        args = {'walk_dist', 'walk_time'}
        if contains_arg(line, args):
            if self.__location is None:
                log.critical("Walking Distance Matrix DTS were detected but "
                             + " no location was set!")
                log.critical("Please either remove the DTS, set a location, "
                             + "or disable the alarm and try again.")
                sys.exit(1)
            if self.__loc_service is None:
                log.critical("Walking Distance Matrix DTS were detected "
                             + "but no API key was provided!")
                log.critical("Please either remove the DTS, add an API key, "
                             + "or disable the alarm and try again.")
                sys.exit(1)
            self.__loc_service.enable_walking_data()

        # Biking Dist Matrix
        args = {'bike_dist', 'bike_time'}
        if contains_arg(line, args):
            if self.__location is None:
                log.critical("Biking Distance Matrix DTS were detected but "
                             + " no location was set!")
                log.critical("Please either remove the DTS, set a location, "
                             + " or disable the alarm and try again.")
                sys.exit(1)
            if self.__loc_service is None:
                log.critical("Biking Distance Matrix DTS were detected "
                             + "  but no API key was provided!")
                log.critical("Please either remove the DTS, add an API key, "
                             + " or disable the alarm and try again.")
                sys.exit(1)
            self.__loc_service.enable_biking_data()

        # Driving Dist Matrix
        args = {'drive_dist', 'drive_time'}
        if contains_arg(line, args):
            if self.__location is None:
                log.critical("Driving Distance Matrix DTS were detected but "
                             + "no location was set!")
                log.critical("Please either remove the DTS, set a location, "
                             + "or disable the alarm and try again.")
                sys.exit(1)
            if self.__loc_service is None:
                log.critical("Driving Distance Matrix DTS were detected but "
                             + "no API key was provided!")
                log.critical("Please either remove the DTS, add an API key, "
                             + " or disable the alarm and try again.")
                sys.exit(1)
            self.__loc_service.enable_driving_data()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HANDLE EVENTS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # Start it up
    def start(self):
        self.__process = gipc.start_process(
            target=self.run, args=(), name=self.__name)

    def setup_in_process(self):
        # Set up signal handlers for graceful exit
        gevent.signal(gevent.signal.SIGINT, self.stop)
        gevent.signal(gevent.signal.SIGTERM, self.stop)

        # Update config
        config['TIMEZONE'] = self.__timezone
        config['API_KEY'] = self.__google_key
        config['UNITS'] = self.__units
        config['DEBUG'] = self.__debug
        config['ROOT_PATH'] = os.path.abspath(
            "{}/..".format(os.path.dirname(__file__)))

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
                event = self.__queue.get(block=True, timeout=5)
            except Queue.Empty:
                # Check if the process should exit process
                if self.__event.is_set():
                    break
                # Explict context yield
                gevent.sleep(0)
                continue

            try:
                kind = type(event)
                log.debug("Processing event: %s", event.id)
                if kind == Events.MonEvent:
                    self.process_monster(event)
                elif kind == Events.StopEvent:
                    self.process_pokestop(event)
                elif kind == Events.GymEvent:
                    self.process_gym(event)
                elif kind == Events.EggEvent:
                    self.process_egg(event)
                elif kind == Events.RaidEvent:
                    self.process_raid(event)
                else:
                    log.error("!!! Manager does not support "
                              + "{} events!".format(kind))
                log.debug("Finished event: %s", event.id)
            except Exception as e:
                log.error("Encountered error during processing: "
                          + "{}: {}".format(type(e).__name__, e))
                log.debug("Stack trace: \n {}".format(traceback.format_exc()))
            # Explict context yield
            gevent.sleep(0)
        # Save cache and exit
        self.__cache.clean_and_save()
        exit(0)

    # Set the location of the Manager
    def set_location(self, location):
        # Regex for Lat,Lng coordinate
        prog = re.compile("^(-?\d+\.\d+)[,\s]\s*(-?\d+\.\d+?)$")
        res = prog.match(location)
        if res:  # If location is in a Lat,Lng coordinate
            self.__location = [float(res.group(1)), float(res.group(2))]
        else:
            if self.__loc_service is None:  # Check if key was provided
                log.error("Unable to find location coordinates by name - "
                          + "no Google API key was provided.")
                return None
            self.__location = self.__loc_service.get_location_from_name(
                location)

        if self.__location is None:
            log.error("Unable to set location - "
                      + "Please check your settings and try again.")
            sys.exit(1)
        else:
            log.info("Location successfully set to '{},{}'.".format(
                self.__location[0], self.__location[1]))

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

    # Process new Monster data and decide if a notification needs to be sent
    def process_monster(self, mon):
        # type: (Events.MonEvent) -> None
        """ Process a monster event and notify alarms if it passes. """

        # Make sure that monsters are enabled
        if self.__mons_enabled is False:
            log.debug("Monster ignored: monster notifications are disabled.")
            return

        # Set the name for this event so we can log rejects better
        mon.name = self.__locale.get_pokemon_name(mon.monster_id)

        # Skip if previously processed
        if self.__cache.get_pokemon_expiration(mon.enc_id) is not None:
            log.debug("{} monster was skipped because it was previously "
                      "processed.".format(mon.name))
            return
        self.__cache.update_pokemon_expiration(
            mon.enc_id, mon.disappear_time)

        # Check the time remaining
        seconds_left = (mon.disappear_time
                        - datetime.utcnow()).total_seconds()
        if seconds_left < self.__time_limit:
            log.debug("{} monster was skipped because only {} seconds remained"
                      "".format(mon.name, seconds_left))
            return

        # Calculate distance
        if self.__location is not None:
            mon.distance = get_earth_dist([mon.lat, mon.lng], self.__location)

        # Check the Filters
        passed = False
        for name, filt in self.__mon_filters.iteritems():
            passed = filt.check_event(mon)
            if passed is True:  # continue to notification if we find a match
                break
        if not passed:  # Monster was rejected by all filters
            return

        # Generate the DTS for the event
        dts = mon.generate_dts(self.__locale)
        if self.__loc_service:
            self.__loc_service.add_optional_arguments(
                self.__location, [mon.lat, mon.lng], dts)

        if self.__quiet is False:
            log.info("{} monster notification has been triggered!".format(
                mon.name))

        threads = []
        # Spawn notifications in threads so they can work in background
        for alarm in self.__alarms:
            threads.append(gevent.spawn(alarm.pokemon_alert, dts))
        gevent.sleep(0)  # explict context yield

        for thread in threads:
            thread.join()

    def process_pokestop(self, stop):
        # type: (Events.StopEvent) -> None
        """ Process a monster event and notify alarms if it passes. """

        # Make sure that monsters are enabled
        if self.__stops_enabled is False:
            log.debug("Stop ignored: stop notifications are disabled.")
            return

        # Skip if previously processed
        if self.__cache.get_pokestop_expiration(stop.stop_id) is not None:
            log.debug("Stop {} was skipped because it was previously "
                      "processed.".format(stop.name))
            return
        self.__cache.update_pokestop_expiration(stop.stop_id, stop.expiration)

        # Check the time remaining
        seconds_left = (stop.expiration - datetime.utcnow()).total_seconds()
        if seconds_left < self.__time_limit:
            log.debug("Stop {} was skipped because only {} seconds remained"
                      "".format(stop.name, seconds_left))
            return

        # Calculate distance
        if self.__location is not None:
            stop.distance = get_earth_dist(
                [stop.lat, stop.lng], self.__location)

        # Check the Filters
        passed = False
        for name, filt in self.__stop_filters.iteritems():
            passed = filt.check_event(stop)
            if passed is True:  # continue to notification if we find a match
                break
        if not passed:  # Stop was rejected by all filters
            return

        # Generate the DTS for the event
        dts = stop.generate_dts(self.__locale)
        if self.__loc_service:
            self.__loc_service.add_optional_arguments(
                self.__location, [stop.lat, stop.lng], dts)

        if self.__quiet is False:
            log.info("Stop {} notification has been triggered!".format(
                stop.name))

        threads = []
        # Spawn notifications in threads so they can work in background
        for alarm in self.__alarms:
            threads.append(gevent.spawn(alarm.pokestop_alert, dts))
        gevent.sleep(0)  # explict context yield

        for thread in threads:
            thread.join()

    def process_gym(self, gym):
        gym_id = gym['id']

        # Update Gym details (if they exist)
        self.__cache.update_gym_info(
            gym_id, gym['name'], gym['description'], gym['url'])

        # Extract some basic information
        to_team_id = gym['new_team_id']
        from_team_id = self.__cache.get_gym_team(gym_id)

        # Ignore changes to neutral
        if self.__gym_filters['ignore_neutral'] and to_team_id == 0:
            log.debug("Gym update ignored: changed to neutral")
            return

        # Update gym's last known team
        self.__cache.update_gym_team(gym_id, to_team_id)

        # Check if notifications are on
        if self.__gym_filters['enabled'] is False:
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

        filters = self.__gym_filters['filters']
        passed = False
        for filt_ct in range(len(filters)):
            filt = filters[filt_ct]
            # Check the distance from the set location
            if dist != 'unkn':
                if filt.check_dist(dist) is False:
                    if self.__quiet is False:
                        log.info("Gym rejected: distance ({:.2f})"
                                 " was not in range"
                                 " {:.2f} to {:.2f} (F #{})".format(
                                     dist, filt.min_dist,
                                     filt.max_dist, filt_ct))
                    continue
            else:
                log.debug("Gym dist was not checked because the manager "
                          "has no location set.")

            # Check the old team
            if filt.check_from_team(from_team_id) is False:
                if self.__quiet is False:
                    log.info("Gym rejected: {} as old team is not correct "
                             " (F #{})".format(old_team, filt_ct))
                continue
            # Check the new team
            if filt.check_to_team(to_team_id) is False:
                if self.__quiet is False:
                    log.info("Gym rejected: {} as current team is not correct "
                             "(F #{})".format(cur_team, filt_ct))
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
            log.debug("Gym inside geofences was not checked because "
                      " no geofences were set.")

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
            self.__loc_service.add_optional_arguments(
                self.__location, [lat, lng], gym)

        if self.__quiet is False:
            log.info("Gym ({}) notification has been "
                     "triggered!".format(gym_id))

        threads = []
        # Spawn notifications in threads so they can work in background
        for alarm in self.__alarms:
            threads.append(gevent.spawn(alarm.gym_alert, gym))
            gevent.sleep(0)  # explict context yield

        for thread in threads:
            thread.join()

    def process_egg(self, egg):
        # Quick check for enabled
        if self.__egg_filters['enabled'] is False:
            log.debug("Egg ignored: notifications are disabled.")
            return

        gym_id = egg['id']
        gym_info = self.__cache.get_gym_info(gym_id)

        # Check if egg has been processed yet
        if self.__cache.get_egg_expiration(gym_id) is not None:
            if self.__quiet is False:
                log.info("Egg {} ignored - previously "
                         "processed.".format(gym_id))
            return

        # Update egg hatch
        self.__cache.update_egg_expiration(gym_id, egg['raid_begin'])

        # don't alert about (nearly) hatched eggs
        seconds_left = (egg['raid_begin'] - datetime.utcnow()).total_seconds()
        if seconds_left < self.__time_limit:
            if self.__quiet is False:
                log.info("Egg {} ignored. Egg hatch in {} seconds".format(
                    gym_id, seconds_left))
            return

        lat, lng = egg['lat'], egg['lng']
        dist = get_earth_dist([lat, lng], self.__location)

        # Check if egg gym filter has a contains field and if so check it
        if len(self.__egg_filters['contains']) > 0:
            log.debug("Egg gymname_contains "
                      "filter: '{}'".format(self.__egg_filters['contains']))
            log.debug("Egg Gym Name is '{}'".format(gym_info['name'].lower()))
            log.debug("Egg Gym Info is '{}'".format(gym_info))
            if not any(x in gym_info['name'].lower()
                       for x in self.__egg_filters['contains']):
                log.info("Egg {} ignored: gym name did not match the "
                         "gymname_contains "
                         "filter.".format(gym_id))
                return

        # Check if raid is in geofences
        egg['geofence'] = self.check_geofences('Raid', lat, lng)
        if len(self.__geofences) > 0 and egg['geofence'] == 'unknown':
            if self.__quiet is False:
                log.info("Egg {} ignored: located outside "
                         "geofences.".format(gym_id))
            return
        else:
            log.debug("Egg inside geofence was not checked because no "
                      "geofences were set.")

        # check if the level is in the filter range or if we are ignoring eggs
        passed = self.check_egg_filter(self.__egg_filters, egg)

        if not passed:
            log.debug("Egg {} did not pass filter check".format(gym_id))
            return

        if self.__loc_service:
            self.__loc_service.add_optional_arguments(
                self.__location, [lat, lng], egg)

        if self.__quiet is False:
            log.info("Egg ({})  notification has been "
                     "triggered!").format(gym_id)

        time_str = get_time_as_str(egg['raid_end'], self.__timezone)
        start_time_str = get_time_as_str(egg['raid_begin'], self.__timezone)

        # team id saved in self.__gym_hist when processing gym
        team_id = self.__cache.get_gym_team(gym_id)

        egg.update({
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
            'team_id': team_id,
            'team_name': self.__locale.get_team_name(team_id),
            'team_leader': self.__locale.get_leader_name(team_id)
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
        if self.__raid_filters['enabled'] is False:
            log.debug("Raid ignored: notifications are disabled.")
            return

        gym_id = raid['id']
        gym_info = self.__cache.get_gym_info(gym_id)

        pkmn_id = raid['pkmn_id']
        raid_end = raid['raid_end']

        # Check if raid has been processed
        if self.__cache.get_raid_expiration(gym_id) is not None:
            if self.__quiet is False:
                log.info("Raid {} ignored. Was previously "
                         "processed.").format(gym_id)
            return

        self.__cache.update_raid_expiration(gym_id, raid_end)
        log.info(self.__cache.get_raid_expiration(gym_id))
        # don't alert about expired raids
        seconds_left = (raid_end - datetime.utcnow()).total_seconds()
        if seconds_left < self.__time_limit:
            if self.__quiet is False:
                log.info("Raid {} ignored. Only {} seconds left.".format(
                    gym_id, seconds_left))
            return

        lat, lng = raid['lat'], raid['lng']
        dist = get_earth_dist([lat, lng], self.__location)

        # Check if raid gym filter has a contains field and if so check it
        if len(self.__raid_filters['contains']) > 0:
            log.debug("Raid gymname_contains "
                      "filter: '{}'".format(self.__raid_filters['contains']))
            log.debug("Raid Gym Name is '{}'".format(gym_info['name'].lower()))
            log.debug("Raid Gym Info is '{}'".format(gym_info))
            if not any(x in gym_info['name'].lower()
                       for x in self.__raid_filters['contains']):
                log.info("Raid {} ignored: gym name did not match the "
                         "gymname_contains "
                         "filter.".format(gym_id))
                return

        # Check if raid is in geofences
        raid['geofence'] = self.check_geofences('Raid', lat, lng)
        if len(self.__geofences) > 0 and raid['geofence'] == 'unknown':
            if self.__quiet is False:
                log.info("Raid {} ignored: located outside "
                         "geofences.".format(gym_id))
            return
        else:
            log.debug("Raid inside geofence was not checked "
                      " because no geofences were set.")

        quick_id = raid['quick_id']
        charge_id = raid['charge_id']

        #  check filters for pokemon
        name = self.__locale.get_pokemon_name(pkmn_id)

        if pkmn_id not in self.__raid_filters['filters']:
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

        filters = self.__raid_filters['filters'][pkmn_id]
        passed = self.check_pokemon_filter(filters, raid_pkmn, dist)
        # If we didn't pass any filters
        if not passed:
            log.debug("Raid {} did not pass pokemon check".format(gym_id))
            return

        if self.__loc_service:
            self.__loc_service.add_optional_arguments(
                self.__location, [lat, lng], raid)

        if self.__quiet is False:
            log.info("Raid ({}) notification "
                     "has been triggered!".format(gym_id))

        time_str = get_time_as_str(
            raid['raid_end'], self.__timezone)
        start_time_str = get_time_as_str(raid['raid_begin'], self.__timezone)

        # team id saved in self.__gym_hist when processing gym
        team_id = self.__cache.get_gym_team(gym_id)
        form_id = raid_pkmn['form_id']
        form = self.__locale.get_form_name(pkmn_id, form_id)
        min_cp, max_cp = get_pokemon_cp_range(pkmn_id, 20)

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
            'form_id_or_empty': '' if form_id == '?'
                                else '{:03}'.format(form_id),
            'form': form,
            'form_or_empty': '' if form == 'unknown' else form,
            'team_id': team_id,
            'team_name': self.__locale.get_team_name(team_id),
            'team_leader': self.__locale.get_leader_name(team_id),
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
                log.debug("{} is not in geofence {}".format(
                    name, gf.get_name()))
        return 'unknown'

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

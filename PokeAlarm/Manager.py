# Standard Library Imports
from datetime import datetime, timedelta
import gevent
import logging
import json
import multiprocessing
import traceback
import re
import sys
# 3rd Party Imports
import gipc
import googlemaps
# Local Imports
from . import config
from Filters import load_pokemon_section, load_pokestop_section, load_gym_section, load_egg_section, \
    load_raid_section
from Locale import Locale
from Utils import get_cardinal_dir, get_dist_as_str, get_earth_dist, get_path, get_time_as_str, \
    require_and_remove_key, parse_boolean, contains_arg
from Geofence import load_geofence_file, Geofence

log = logging.getLogger('Manager')


class Manager(object):
    def __init__(self, name, google_key, locale, units, timezone, time_limit, max_attempts, location, quiet,
                 filter_file, geofence_file, alarm_file, debug):
        # Set the name of the Manager
        self.__name = str(name).lower()
        log.info("----------- Manager '{}' is being created.".format(self.__name))
        self.__debug = debug

        # Get the Google Maps API
        self.__google_key = google_key
        self.__gmaps_client = \
            googlemaps.Client(key=self.__google_key, timeout=3, retry_timeout=4) if google_key is not None else None
        self.__api_req = {'REVERSE_LOCATION': False, 'WALK_DIST': False, 'BIKE_DIST': False, 'DRIVE_DIST': False}

        # Setup the language-specific stuff
        self.__locale = Locale(locale)

        self.__units = units  # type of unit used for distances
        self.__timezone = timezone  # timezone for time calculations
        self.__time_limit = time_limit  # Minimum time remaining for stops and pokemon
        self.__latlng = self.get_lat_lng_from_name(location)  # Array with Lat, Lng for the Manager
        # Quiet mode
        self.__quiet = quiet

        # Load and Setup the Pokemon Filters
        self.__pokemon_settings, self.__pokestop_settings, self.__gym_settings = {}, {}, {}
        self.__raid_settings, self.__egg_settings = {}, {}
        self.__pokemon_hist, self.__pokestop_hist, self.__gym_hist, self.__raid_hist = {}, {}, {}, {}
        self.__gym_info = {}
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
        self.__process = None

        log.info("----------- Manager '{}' successfully created.".format(self.__name))

    ############################################## CALLED BY MAIN PROCESS ##############################################

    # Update the object into the queue
    def update(self, obj):
        self.__queue.put(obj)

    # Get the name of this Manager
    def get_name(self):
        return self.__name

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
                    _type = require_and_remove_key('type', alarm, "Alarm objects in Alarms file.")
                    self.set_optional_args(str(alarm))
                    if _type == 'discord':
                        from Discord import DiscordAlarm
                        self.__alarms.append(DiscordAlarm(alarm, max_attempts, self.__google_key))
                    elif _type == 'facebook_page':
                        from FacebookPage import FacebookPageAlarm
                        self.__alarms.append(FacebookPageAlarm(alarm))
                    elif _type == 'pushbullet':
                        from Pushbullet import PushbulletAlarm
                        self.__alarms.append(PushbulletAlarm(alarm))
                    elif _type == 'slack':
                        from Slack import SlackAlarm
                        self.__alarms.append(SlackAlarm(alarm, self.__google_key))
                    elif _type == 'telegram':
                        from Telegram import TelegramAlarm
                        self.__alarms.append(TelegramAlarm(alarm))
                    elif _type == 'twilio':
                        from Twilio import TwilioAlarm
                        self.__alarms.append(TwilioAlarm(alarm))
                    elif _type == 'twitter':
                        from Twitter import TwitterAlarm
                        self.__alarms.append(TwitterAlarm(alarm))
                    else:
                        log.error("Alarm type not found: " + alarm['type'])
                        log.error("Please consult the PokeAlarm documentation accepted Alarm Types")
                        sys.exit(1)
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

    # Returns true if string contains an argument that requires
    def set_optional_args(self, line):
        # Reverse Location
        args = {'street', 'street_num', 'address', 'postal',
                'neighborhood', 'sublocality', 'city', 'county', 'state', 'country'}
        self.__api_req['REVERSE_LOCATION'] = self.__api_req['REVERSE_LOCATION'] or contains_arg(line, args)
        log.debug("REVERSE_LOCATION set to %s" % self.__api_req['REVERSE_LOCATION'])

        # Walking Time
        args = {'walk_dist', 'walk_time'}
        self.__api_req['WALK_DIST'] = self.__api_req['WALK_DIST'] or contains_arg(line, args)
        log.debug("WALK_DIST set to %s" % self.__api_req['WALK_DIST'])

        # Biking Time
        args = {'bike_dist', 'bike_time'}
        self.__api_req['BIKE_DIST'] = self.__api_req['BIKE_DIST'] or contains_arg(line, args)
        log.debug("BIKE_DIST set to %s" % self.__api_req['BIKE_DIST'])

        # Driving Time
        args = {'drive_dist', 'drive_time'}
        self.__api_req['DRIVE_DIST'] = self.__api_req['DRIVE_DIST'] or contains_arg(line, args)
        log.debug("DRIVE_DIST set to %s" % self.__api_req['DRIVE_DIST'])

    ####################################################################################################################

    ################################################## HANDLE EVENTS  ##################################################

    # Start it up
    def start(self):
        self.__process = gipc.start_process(target=self.run, args=(), name=self.__name)

    def setup_in_process(self):
        # Update config
        config['TIMEZONE'] = self.__timezone
        config['API_KEY'] = self.__google_key
        config['UNITS'] = self.__units
        config['DEBUG'] = self.__debug

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
            # Get next object to process
            obj = self.__queue.get(block=True)
            # Clean out visited every 3 minutes
            if datetime.utcnow() - last_clean > timedelta(minutes=3):
                log.debug("Cleaning history...")
                self.clean_hist()
                last_clean = datetime.utcnow()
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

    # Clean out the expired objects from histories (to prevent oversized sets)
    def clean_hist(self):
        for dict_ in (self.__pokemon_hist, self.__pokestop_hist):
            old = []
            for id_ in dict_:  # Gather old events
                if dict_[id_] < datetime.utcnow():
                    old.append(id_)
            for id_ in old:  # Remove gathered events
                del dict_[id_]

        # raid history has a different structure because it saves both expire time and pokemon
        old = []
        for id_ in self.__raid_hist:
            if self.__raid_hist[id_]['raid_end'] < datetime.utcnow():
                old.append(id_)
        for id_ in old:  # Remove expired raids
            del self.__raid_hist[id_]

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
        id_ = pkmn['id']
        pkmn_id = pkmn['pkmn_id']
        name = self.__locale.get_pokemon_name(pkmn_id)

        # Check for previously processed
        if id_ in self.__pokemon_hist:
            log.debug("{} was skipped because it was previously processed.".format(name))
            return
        self.__pokemon_hist[id_] = pkmn['disappear_time']

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
        dist = get_earth_dist([lat, lng], self.__latlng)

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

        pkmn.update({
            'pkmn': name,
            "dist": get_dist_as_str(dist) if dist != 'unkn' else 'unkn',
            'time_left': time_str[0],
            '12h_time': time_str[1],
            '24h_time': time_str[2],
            'dir': get_cardinal_dir([lat, lng], self.__latlng),
            'iv_0': "{:.0f}".format(iv) if iv != '?' else '?',
            'iv': "{:.1f}".format(iv) if iv != '?' else '?',
            'iv_2': "{:.2f}".format(iv) if iv != '?' else '?',
            'quick_move': self.__locale.get_move_name(quick_id),
            'charge_move': self.__locale.get_move_name(charge_id),
            'form': self.__locale.get_form_name(pkmn_id, pkmn['form_id'])
        })
        self.add_optional_travel_arguments(pkmn)

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

        id_ = stop['id']

        # Check for previously processed
        if id_ in self.__pokestop_hist:
            log.debug("Pokestop was skipped because it was previously processed.")
            return
        self.__pokestop_hist[id_] = stop['expire_time']

        # Check the time remaining
        seconds_left = (stop['expire_time'] - datetime.utcnow()).total_seconds()
        if seconds_left < self.__time_limit:
            if self.__quiet is False:
                log.info("Pokestop ({}) ignored: only {} seconds remaining.".format(id_, seconds_left))
            return

        # Extract some basic information
        lat, lng = stop['lat'], stop['lng']
        dist = get_earth_dist([lat, lng], self.__latlng)
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
            'dir': get_cardinal_dir([lat, lng], self.__latlng),
        })
        self.add_optional_travel_arguments(stop)

        if self.__quiet is False:
            log.info("Pokestop ({}) notification has been triggered!".format(id_))

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
        if gym_id not in self.__gym_info or gym['name'] != 'unknown':
            self.__gym_info[gym_id] = {
                "name": gym['name'],
                "description": gym['description'],
                "url": gym['url']
            }

        if self.__gym_settings['enabled'] is False:
            log.debug("Gym ignored: notifications are disabled.")
            return

        # Extract some basic information
        to_team_id = gym['new_team_id']
        from_team_id = self.__gym_hist.get(gym_id)

        # Doesn't look like anything to me
        if to_team_id == from_team_id:
            log.debug("Gym ignored: no change detected")
            return
        # Ignore changes to neutral
        if self.__gym_settings['ignore_neutral'] and to_team_id == 0:
            log.debug("Gym update ignored: changed to neutral")
            return
        # Update gym's last known team
        self.__gym_hist[gym_id] = to_team_id

        # Ignore first time updates
        if from_team_id is None:
            log.debug("Gym update ignored: first time seeing this gym")
            return

        # Get some more info out used to check filters
        lat, lng = gym['lat'], gym['lng']
        dist = get_earth_dist([lat, lng], self.__latlng)
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

        gym_info = self.__gym_info.get(gym_id, {})

        gym.update({
            "gym_name": gym_info.get('name', 'unknown'),
            "gym_description": gym_info.get('description', 'unknown'),
            "gym_url": gym_info.get('url', 'https://raw.githubusercontent.com/kvangent/PokeAlarm/master/icons/gym_0.png'),
            "dist": get_dist_as_str(dist),
            'dir': get_cardinal_dir([lat, lng], self.__latlng),
            'new_team': cur_team,
            'new_team_id': to_team_id,
            'old_team': old_team,
            'old_team_id': from_team_id,
            'new_team_leader': self.__locale.get_leader_name(to_team_id),
            'old_team_leader': self.__locale.get_leader_name(from_team_id)
        })
        self.add_optional_travel_arguments(gym)

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

        raid_end = egg['raid_end']

        # raid history will contains any raid processed
        if gym_id in self.__raid_hist:
            old_raid_end = self.__raid_hist[gym_id]['raid_end']
            if old_raid_end == raid_end:
                if self.__quiet is False:
                    log.info("Raid {} ignored. Was previously processed.".format(gym_id))
                return

        self.__raid_hist[gym_id] = dict(raid_end=raid_end, pkmn_id=0)

        # don't alert about (nearly) hatched eggs
        seconds_left = (egg['raid_begin'] - datetime.utcnow()).total_seconds()
        if seconds_left < self.__time_limit:
            if self.__quiet is False:
                log.info("Egg {} ignored. Egg hatch in {} seconds".format(gym_id, seconds_left))
            return

        lat, lng = egg['lat'], egg['lng']
        dist = get_earth_dist([lat, lng], self.__latlng)

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

        self.add_optional_travel_arguments(egg)

        if self.__quiet is False:
            log.info("Egg ({}) notification has been triggered!".format(gym_id))

        time_str = get_time_as_str(egg['raid_end'], self.__timezone)
        start_time_str = get_time_as_str(egg['raid_begin'], self.__timezone)

        gym_info = self.__gym_info.get(gym_id, {})

        egg.update({
            "gym_name": gym_info.get('name', 'unknown'),
            "gym_description": gym_info.get('description', 'unknown'),
            "gym_url": gym_info.get('url', 'https://raw.githubusercontent.com/kvangent/PokeAlarm/master/icons/gym_0.png'),
            'time_left': time_str[0],
            '12h_time': time_str[1],
            '24h_time': time_str[2],
            'begin_time_left': start_time_str[0],
            'begin_12h_time': start_time_str[1],
            'begin_24h_time': start_time_str[2],
            "dist": get_dist_as_str(dist),
            'dir': get_cardinal_dir([lat, lng], self.__latlng)
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

        # raid history will contain the end date and also the pokemon if it has hatched
        if gym_id in self.__raid_hist:
            old_raid_end = self.__raid_hist[gym_id]['raid_end']
            old_raid_pkmn = self.__raid_hist[gym_id].get('pkmn_id', 0)
            if old_raid_end == raid_end:
                if old_raid_pkmn == pkmn_id:  # raid with same end time exists and it has same pokemon id, skip it
                    if self.__quiet is False:
                        log.info("Raid {} ignored. Was previously processed.".format(gym_id))
                    return

        self.__raid_hist[gym_id] = dict(raid_end=raid_end, pkmn_id=pkmn_id)

        # don't alert about expired raids
        seconds_left = (raid_end - datetime.utcnow()).total_seconds()
        if seconds_left < self.__time_limit:
            if self.__quiet is False:
                log.info("Raid {} ignored. Only {} seconds left.".format(gym_id, seconds_left))
            return

        lat, lng = raid['lat'], raid['lng']
        dist = get_earth_dist([lat, lng], self.__latlng)

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

        self.add_optional_travel_arguments(raid)

        if self.__quiet is False:
            log.info("Raid ({}) notification has been triggered!".format(gym_id))

        time_str = get_time_as_str(raid['raid_end'], self.__timezone)
        start_time_str = get_time_as_str(raid['raid_begin'], self.__timezone)

        gym_info = self.__gym_info.get(gym_id, {})

        raid.update({
            'pkmn': name,
            "gym_name": gym_info.get('name', 'unknown'),
            "gym_description": gym_info.get('description', 'unknown'),
            "gym_url": gym_info.get('url', 'https://raw.githubusercontent.com/kvangent/PokeAlarm/master/icons/gym_0.png'),
            'time_left': time_str[0],
            '12h_time': time_str[1],
            '24h_time': time_str[2],
            'begin_time_left': start_time_str[0],
            'begin_12h_time': start_time_str[1],
            'begin_24h_time': start_time_str[2],
            "dist": get_dist_as_str(dist),
            'dir': get_cardinal_dir([lat, lng], self.__latlng),
            'quick_move': self.__locale.get_move_name(quick_id),
            'charge_move': self.__locale.get_move_name(charge_id),
            'form': self.__locale.get_form_name(pkmn_id, raid_pkmn['form_id'])
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
                log.debug("{} is in geofence {}!".format(name, gf.name))
                return gf.name
            else:
                log.debug("{} is not in geofence {}".format(name, gf.name))
        return 'unknown'

    # Retrieve optional requirements
    def add_optional_travel_arguments(self, info):
        lat, lng = info['lat'], info['lng']
        if self.__api_req['REVERSE_LOCATION']:
            info.update(**self.reverse_location(lat, lng))
        if self.__api_req['WALK_DIST']:
            info.update(**self.get_walking_data(lat, lng))
        if self.__api_req['BIKE_DIST']:
            info.update(**self.get_biking_data(lat, lng))
        if self.__api_req['DRIVE_DIST']:
            info.update(**self.get_driving_data(lat, lng))

    ####################################################################################################################

    ############################################## REQUIRES GOOGLE API KEY #############################################

    # Returns the LAT,LNG of a location given by either a name or coordinates
    def get_lat_lng_from_name(self, location_name):
        if location_name is None:
            return None
        try:
            prog = re.compile("^(-?\d+\.\d+)[,\s]\s*(-?\d+\.\d+?)$")
            res = prog.match(location_name)
            latitude, longitude = None, None
            if res:
                latitude, longitude = float(res.group(1)), float(res.group(2))
            elif location_name:
                if self.__gmaps_client is None:  # Check if key was provided
                    log.error("No Google Maps API key provided - unable to find location by name.")
                    return None
                result = self.__gmaps_client.geocode(location_name)
                loc = result[0]['geometry']['location']  # Get the first (most likely) result
                latitude, longitude = loc.get("lat"), loc.get("lng")
            log.info("Coordinates found for '{}': {:f},{:f}".format(location_name, latitude, longitude))
            return [latitude, longitude]
        except Exception as e:
            log.error("Encountered error while getting error by name ({}: {})".format(type(e).__name__, e))
            log.debug("Stack trace: \n {}".format(traceback.format_exc()))
            log.error("Encounted error looking for location {}.".format(location_name)
                      + "Please make sure your location is in the correct format")
            sys.exit(1)

    # Returns the name of the location based on lat and lng
    def reverse_location(self, lat, lng):
        # Set defaults in case something goes wrong
        details = {
            'street_num': 'unkn', 'street': 'unknown', 'address': 'unknown', 'postal': 'unknown',
            'neighborhood': 'unknown', 'sublocality': 'unknown', 'city': 'unknown',
            'county': 'unknown', 'state': 'unknown', 'country': 'country'
        }
        if self.__gmaps_client is None:  # Check if key was provided
            log.error("No Google Maps API key provided - unable to reverse geocode.")
            return details
        try:
            result = self.__gmaps_client.reverse_geocode((lat, lng))[0]
            loc = {}
            for item in result['address_components']:
                for category in item['types']:
                    loc[category] = item['short_name']
            details['street_num'] = loc.get('street_number', 'unkn')
            details['street'] = loc.get('route', 'unkn')
            details['address'] = "{} {}".format(details['street_num'], details['street'])
            details['postal'] = loc.get('postal_code', 'unkn')
            details['neighborhood'] = loc.get('neighborhood', "unknown")
            details['sublocality'] = loc.get('sublocality', "unknown")
            details['city'] = loc.get('locality', loc.get('postal_town', 'unknown'))
            details['county'] = loc.get('administrative_area_level_2', 'unknown')
            details['state'] = loc.get('administrative_area_level_1', 'unknown')
            details['country'] = loc.get('country', 'unknown')
        except Exception as e:
            log.error("Encountered error while getting reverse location data ({}: {})".format(type(e).__name__, e))
            log.debug("Stack trace: \n {}".format(traceback.format_exc()))
        return details

    # Returns a set with walking dist and walking duration via Google Distance Matrix API
    def get_walking_data(self, lat, lng):
        data = {'walk_dist': "unknown", 'walk_time': "unknown"}
        if self.__latlng is None:
            log.error("No location has been set. Unable to get walking data.")
            return data
        origin = "{},{}".format(self.__latlng[0], self.__latlng[1])
        dest = "{},{}".format(lat, lng)
        try:
            result = self.__gmaps_client.distance_matrix(origin, dest, mode='walking', units=config['UNITS'])
            result = result.get('rows')[0].get('elements')[0]
            data['walk_dist'] = result.get('distance').get('text').encode('utf-8')
            data['walk_time'] = result.get('duration').get('text').encode('utf-8')
        except Exception as e:
            log.error("Encountered error while getting walking data ({}: {})".format(type(e).__name__, e))
            log.debug("Stack trace: \n {}".format(traceback.format_exc()))
        return data

    # Returns a set with biking dist and biking duration via Google Distance Matrix API
    def get_biking_data(self, lat, lng):
        data = {'bike_dist': "unknown", 'bike_time': "unknown"}
        if self.__latlng is None:
            log.error("No location has been set. Unable to get biking data.")
            return data
        origin = "{},{}".format(self.__latlng[0], self.__latlng[1])
        dest = "{},{}".format(lat, lng)
        try:
            result = self.__gmaps_client.distance_matrix(origin, dest, mode='bicycling', units=config['UNITS'])
            result = result.get('rows')[0].get('elements')[0]
            data['bike_dist'] = result.get('distance').get('text').encode('utf-8')
            data['bike_time'] = result.get('duration').get('text').encode('utf-8')
        except Exception as e:
            log.error("Encountered error while getting biking data ({}: {})".format(type(e).__name__, e))
            log.debug("Stack trace: \n {}".format(traceback.format_exc()))
        return data

    # Returns a set with driving dist and biking duration via Google Distance Matrix API
    def get_driving_data(self, lat, lng):
        data = {'drive_dist': "unknown", 'drive_time': "unknown"}
        if self.__latlng is None:
            log.error("No location has been set. Unable to get biking data.")
            return data
        origin = "{},{}".format(self.__latlng[0], self.__latlng[1])
        dest = "{},{}".format(lat, lng)
        try:
            result = self.__gmaps_client.distance_matrix(origin, dest, mode='driving', units=config['UNITS'])
            result = result.get('rows')[0].get('elements')[0]
            data['drive_dist'] = result.get('distance').get('text').encode('utf-8')
            data['drive_time'] = result.get('duration').get('text').encode('utf-8')
        except Exception as e:
            log.error("Encountered error while getting driving data ({}: {})".format(type(e).__name__, e))
            log.debug("Stack trace: \n {}".format(traceback.format_exc()))
        return data

        ####################################################################################################################

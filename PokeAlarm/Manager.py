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
from Utils import (get_earth_dist, get_path, require_and_remove_key,
                   parse_boolean, contains_arg)
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
        self.geofences = None
        if str(geofence_file).lower() != 'none':
            self.geofences = load_geofence_file(get_path(geofence_file))
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
            settings = dict(defaults.items() + settings.items())
            try:
                filter_set[name] = filter_type(name, settings)
                log.debug(
                    "Filter '%s' set as the following: %s", name,
                    filter_set[name].to_dict())
            except Exception as e:
                log.error("Encountered error inside filter named '%s'.", name)
                raise e  # Pass the error up
        for key in section:  # Reject leftover parameters
            raise ValueError("'{}' is not a recognized parameter for the "
                             "'{}' section.".format(key, sect_name))
        return filter_set

    # Load in a new filters file
    def load_filter_file(self, file_path):
        try:
            log.info("Loading Filters from file at {}".format(file_path))
            with open(file_path, 'r') as f:
                filters = json.load(f)
            if type(filters) is not dict:
                log.critical("Filters file's must be a JSON object:"
                             " { \"monsters\":{...},... }")
        except ValueError as e:
            log.error("Encountered error while loading Filters:"
                      " {}: {}".format(type(e).__name__, e))
            log.error(
                "PokeAlarm has encountered a 'ValueError' while loading the "
                "Filters file. This typically means the file isn't in the "
                "correct json format. Try loading the file contents into a "
                "json validator.")
            log.debug("Stack trace: \n {}".format(traceback.format_exc()))
            sys.exit(1)
        except IOError as e:
            log.error("Encountered error while loading Filters: "
                      "{}: {}".format(type(e).__name__, e))
            log.error("PokeAlarm was unable to find a filters file "
                      "at {}. Please check that this file exists "
                      "and that PA has read permissions.".format(file_path))
            log.debug("Stack trace: \n {}".format(traceback.format_exc()))
            sys.exit(1)

        try:
            # Load Monsters Section
            log.info("Parsing 'monsters' section.")
            section = filters.pop('monsters', {})
            self.__mons_enabled = bool(section.pop('enabled', True))
            self.__mon_filters = self.load_filter_section(
                section, 'monsters', Filters.MonFilter)

            # Load Stops Section
            log.info("Parsing 'stops' section.")
            section = filters.pop('stops', {})
            self.__stops_enabled = bool(section.pop('enabled', True))
            self.__stop_filters = self.load_filter_section(
                section, 'stops', Filters.StopFilter)

            # Load Gyms Section
            log.info("Parsing 'gyms' section.")
            section = filters.pop('gyms', {})
            self.__gyms_enabled = bool(section.pop('enabled', True))
            self.__ignore_neutral = bool(section.pop('ignore_neutral', False))
            self.__gym_filters = self.load_filter_section(
                section, 'gyms', Filters.GymFilter)

            # Load Eggs Section
            log.info("Parsing 'eggs' section.")
            section = filters.pop('eggs', {})
            self.__eggs_enabled = bool(section.pop('enabled', True))
            self.__egg_filters = self.load_filter_section(
                section, 'eggs', Filters.EggFilter)

            # Load Raids Section
            log.info("Parsing 'raids' section.")
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
                    self.process_stop(event)
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
        for name, f in self.__mon_filters.iteritems():
            passed = f.check_event(mon) and self.check_geofences(f, mon)
            if passed:  # Stop checking
                mon.custom_dts = f.custom_dts
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

    def process_stop(self, stop):
        # type: (Events.StopEvent) -> None
        """ Process a stop event and notify alarms if it passes. """

        # Make sure that stops are enabled
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
        passed = True
        for name, f in self.__stop_filters.iteritems():
            passed = f.check_event(stop) and self.check_geofences(f, stop)
            if passed:  # Stop checking
                stop.custom_dts = f.custom_dts
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
        # type: (Events.GymEvent) -> None
        """ Process a gym event and notify alarms if it passes. """

        # Update Gym details (if they exist)
        self.__cache.update_gym_info(
            gym.gym_id, gym.gym_name, gym.gym_description, gym.gym_image)

        # Ignore changes to neutral
        if self.__ignore_neutral and gym.new_team_id == 0:
            log.debug("%s gym update skipped: new team was neutral")
            return

        # Get the old team and update new team
        gym.old_team_id = self.__cache.get_gym_team(gym.gym_id)
        self.__cache.update_gym_team(gym.gym_id, gym.new_team_id)

        # Check if notifications are on
        if self.__gyms_enabled is False:
            log.debug("Gym ignored: gym notifications are disabled.")
            return

        # Update the cache with the gyms info
        info = self.__cache.get_gym_info(gym.gym_id)
        gym.gym_name = info['name']
        gym.gym_description = info['description']
        gym.gym_image = info['url']

        # Doesn't look like anything to me
        if gym.new_team_id == gym.old_team_id:
            log.debug("%s gym update skipped: no change detected", gym.gym_id)
            return

        # Calculate distance
        if self.__location is not None:
            gym.distance = get_earth_dist([gym.lat, gym.lng], self.__location)

        # Check the Filters
        passed = True
        for name, f in self.__gym_filters.iteritems():
            passed = f.check_event(gym) and self.check_geofences(f, gym)
            if passed:  # Stop checking
                gym.custom_dts = f.custom_dts
                break
        if not passed:  # Gym was rejected by all filters
            return

        # Generate the DTS for the event
        dts = gym.generate_dts(self.__locale)
        dts.update(self.__cache.get_gym_info(gym.gym_id))  # update gym info
        if self.__loc_service:
            self.__loc_service.add_optional_arguments(
                self.__location, [gym.lat, gym.lng], dts)

        if self.__quiet is False:
            log.info(
                "{} gym notification has been triggered!".format(gym.name))

        threads = []
        # Spawn notifications in threads so they can work in background
        for alarm in self.__alarms:
            threads.append(gevent.spawn(alarm.gym_alert, dts))
        gevent.sleep(0)  # explict context yield

        for thread in threads:
            thread.join()

    def process_egg(self, egg):
        # type: (Events.EggEvent) -> None
        """ Process a egg event and notify alarms if it passes. """

        # Update Gym details (if they exist)
        self.__cache.update_gym_info(
            egg.gym_id, egg.gym_name, egg.gym_description, egg.gym_image)

        # Make sure that eggs are enabled
        if self.__eggs_enabled is False:
            log.debug("Egg ignored: egg notifications are disabled.")
            return

        # Skip if previously processed
        if self.__cache.get_egg_expiration(egg.gym_id) is not None:
            log.debug("Egg {} was skipped because it was previously "
                      "processed.".format(egg.name))
            return
        self.__cache.update_egg_expiration(egg.gym_id, egg.hatch_time)

        # Check the time remaining
        seconds_left = (egg.hatch_time - datetime.utcnow()).total_seconds()
        if seconds_left < self.__time_limit:
            log.debug("Egg {} was skipped because only {} seconds remained"
                      "".format(egg.name, seconds_left))
            return

        # Assigned cached info
        info = self.__cache.get_gym_info(egg.gym_id)
        egg.gym_name = info['name']
        egg.gym_description = info['description']
        egg.gym_image = info['url']

        # Calculate distance
        if self.__location is not None:
            egg.distance = get_earth_dist(
                [egg.lat, egg.lng], self.__location)

        # Check the Filters
        passed = True
        for name, f in self.__egg_filters.iteritems():
            passed = f.check_event(egg) and self.check_geofences(f, egg)
            if passed:  # Stop checking
                egg.custom_dts = f.custom_dts
                break
        if not passed:  # Egg was rejected by all filters
            return

        # Generate the DTS for the event
        dts = egg.generate_dts(self.__locale)
        dts.update(self.__cache.get_gym_info(egg.gym_id))  # update gym info
        if self.__loc_service:
            self.__loc_service.add_optional_arguments(
                self.__location, [egg.lat, egg.lng], dts)

        if self.__quiet is False:
            log.info(
                "{} egg notification has been triggered!".format(egg.gym_name))

        threads = []
        # Spawn notifications in threads so they can work in background
        for alarm in self.__alarms:
            threads.append(gevent.spawn(alarm.raid_egg_alert, dts))
        gevent.sleep(0)  # explict context yield

        for thread in threads:
            thread.join()

    def process_raid(self, raid):
        # type: (Events.RaidEvent) -> None
        """ Process a raid event and notify alarms if it passes. """

        # Update Gym details (if they exist)
        self.__cache.update_gym_info(
            raid.gym_id, raid.gym_name, raid.gym_description, raid.gym_image)

        # Make sure that raids are enabled
        if self.__raids_enabled is False:
            log.debug("Raid ignored: raid notifications are disabled.")
            return

        # Skip if previously processed
        if self.__cache.get_raid_expiration(raid.gym_id) is not None:
            log.debug("Raid {} was skipped because it was previously "
                      "processed.".format(raid.name))
            return
        self.__cache.update_raid_expiration(raid.gym_id, raid.raid_end)

        # Check the time remaining
        seconds_left = (raid.raid_end - datetime.utcnow()).total_seconds()
        if seconds_left < self.__time_limit:
            log.debug("Raid {} was skipped because only {} seconds remained"
                      "".format(raid.name, seconds_left))
            return

        # Assigned cached info
        info = self.__cache.get_gym_info(raid.gym_id)
        raid.gym_name = info['name']
        raid.gym_description = info['description']
        raid.gym_image = info['url']

        # Calculate distance
        if self.__location is not None:
            raid.distance = get_earth_dist(
                [raid.lat, raid.lng], self.__location)

        # Check the Filters
        passed = True
        for name, f in self.__raid_filters.iteritems():
            passed = f.check_event(raid) and self.check_geofences(f, raid)
            if passed:  # Stop checking
                raid.custom_dts = f.custom_dts
                break
        if not passed:  # Raid was rejected by all filters
            return

        # Generate the DTS for the event
        dts = raid.generate_dts(self.__locale)
        dts.update(self.__cache.get_gym_info(raid.gym_id))  # update gym info
        if self.__loc_service:
            self.__loc_service.add_optional_arguments(
                self.__location, [raid.lat, raid.lng], dts)

        if self.__quiet is False:
            log.info(
                "{} raid notification triggered!".format(raid.gym_name))

        threads = []
        # Spawn notifications in threads so they can work in background
        for alarm in self.__alarms:
            threads.append(gevent.spawn(alarm.raid_alert, dts))
        gevent.sleep(0)  # explict context yield

        for thread in threads:
            thread.join()

    # Check to see if a notification is within the given range
    def check_geofences(self, f, e):
        """ Returns true if the event passes the filter's geofences. """
        if self.geofences is None or f.geofences is None:  # No geofences set:
            return True
        targets = f.geofences
        if len(targets) == 1 and "all" in targets:
            targets = self.geofences.iterkeys()
        for name in targets:
            gf = self.geofences.get(name)
            if not gf:  # gf doesn't exist
                log.error("Cannot check geofence %s: does not exist!", name)
            elif gf.contains(e.lat, e.lng):  # e in gf
                log.debug("{} is in geofence {}!".format(
                    e.name, gf.get_name()))
                e.geofence = name  # Set the geofence for dts
                return True
            else:  # e not in gf
                log.debug("%s not in %s.", e.name, name)
        f.reject(e, "not in geofences")
        return False

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

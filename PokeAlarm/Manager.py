# Standard Library Imports
import json
import logging
import os
import re
import sys
import traceback
from collections import OrderedDict, namedtuple
from datetime import datetime, timedelta

# 3rd Party Imports
import gevent
from gevent.queue import Queue
from gevent.event import Event

# Local Imports
import Alarms
import Filters
import Events
from Cache import cache_factory
from Geofence import load_geofence_file
from Locale import Locale
from LocationServices import GMaps
from PokeAlarm import Unknown
from Utils import (get_earth_dist, get_path, require_and_remove_key,
                   parse_boolean, get_cardinal_dir)
from . import config
Rule = namedtuple('Rule', ['filter_names', 'alarm_names'])

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
        self._google_key = None
        self._gmaps_service = None
        if str(google_key).lower() != 'none':
            self._google_key = google_key
            self._gmaps_service = GMaps(google_key)
        self._gmaps_reverse_geocode = False
        self._gmaps_distance_matrix = set()

        self._language = locale
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
        self.__mons_enabled, self.__mon_filters = False, OrderedDict()
        self.__stops_enabled, self.__stop_filters = False, OrderedDict()
        self.__gyms_enabled, self.__gym_filters = False, OrderedDict()
        self.__ignore_neutral = False
        self.__eggs_enabled, self.__egg_filters = False, OrderedDict()
        self.__raids_enabled, self.__raid_filters = False, OrderedDict()
        self.load_filter_file(get_path(filter_file))

        # Create the Geofences to filter with from given file
        self.geofences = None
        if str(geofence_file).lower() != 'none':
            self.geofences = load_geofence_file(get_path(geofence_file))
        # Create the alarms to send notifications out with
        self.__alarms = {}
        self.load_alarms_file(get_path(alarm_file), int(max_attempts))

        # Initialize Rules
        self.__mon_rules = {}
        self.__stop_rules = {}
        self.__gym_rules = {}
        self.__egg_rules = {}
        self.__raid_rules = {}

        # Initialize the queue and start the process
        self.__queue = Queue()
        self.__event = Event()
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
        self.__process.join(timeout=20)
        if not self.__process.ready():
            log.warning("Manager {} could not be stopped in time!"
                        " Forcing process to stop.".format(self.__name))
            self.__process.kill(timeout=2, block=True)  # Force stop
        else:
            log.info("Manager {} successfully stopped!".format(self.__name))

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ GMAPS API ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def enable_gmaps_reverse_geocoding(self):
        """Enable GMaps Reverse Geocoding DTS for triggered Events. """
        if not self._gmaps_service:
            raise ValueError("Unable to enable Google Maps Reverse Geocoding."
                             "No GMaps API key has been set.")
        self._gmaps_reverse_geocode = True

    def disable_gmaps_reverse_geocoding(self):
        """Disable GMaps Reverse Geocoding DTS for triggered Events. """
        self._gmaps_reverse_geocode = False

    def enable_gmaps_distance_matrix(self, mode):
        """Enable 'mode' Distance Matrix DTS for triggered Events. """
        if not self.__location:
            raise ValueError("Unable to enable Google Maps Reverse Geocoding."
                             "No Manager location has been set.")
        elif not self._gmaps_service:
            raise ValueError("Unable to enable Google Maps Reverse Geocoding."
                             "No GMaps API key has been provided.")
        elif mode not in GMaps.TRAVEL_MODES:
            raise ValueError("Unable to enable distance matrix mode: "
                             "{} is not a valid mode.".format(mode))
        self._gmaps_distance_matrix.add(mode)

    def disable_gmaps_dm_walking(self, mode):
        """Disable 'mode' Distance Matrix DTS for triggered Events. """
        if mode not in GMaps.TRAVEL_MODES:
            raise ValueError("Unable to disable distance matrix mode: "
                             "Invalid mode specified.")
        self._gmaps_distance_matrix.discard(mode)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ RULES API ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # Add new Monster Rule
    def add_monster_rule(self, name, filters, alarms):
        if name in self.__mon_rules:
            raise ValueError("Unable to add Rule: Monster Rule with the name "
                             "{} already exists!".format(name))

        for filt in filters:
            if filt not in self.__mon_filters:
                raise ValueError("Unable to create Rule: No Monster Filter "
                                 "named {}!".format(filt))

        for alarm in alarms:
            if alarm not in self.__alarms:
                raise ValueError("Unable to create Rule: No Alarm "
                                 "named {}!".format(alarm))

        self.__mon_rules[name] = Rule(filters, alarms)

    # Add new Stop Rule
    def add_stop_rule(self, name, filters, alarms):
        if name in self.__stop_rules:
            raise ValueError("Unable to add Rule: Stop Rule with the name "
                             "{} already exists!".format(name))

        for filt in filters:
            if filt not in self.__stop_filters:
                raise ValueError("Unable to create Rule: No Stop Filter "
                                 "named {}!".format(filt))

        for alarm in alarms:
            if alarm not in self.__alarms:
                raise ValueError("Unable to create Rule: No Alarm "
                                 "named {}!".format(alarm))

        self.__stop_rules[name] = Rule(filters, alarms)

    # Add new Gym Rule
    def add_gym_rule(self, name, filters, alarms):
        if name in self.__gym_rules:
            raise ValueError("Unable to add Rule: Gym Rule with the name "
                             "{} already exists!".format(name))

        for filt in filters:
            if filt not in self.__gym_filters:
                raise ValueError("Unable to create Rule: No Gym Filter "
                                 "named {}!".format(filt))

        for alarm in alarms:
            if alarm not in self.__alarms:
                raise ValueError("Unable to create Rule: No Alarm "
                                 "named {}!".format(alarm))

        self.__gym_rules[name] = Rule(filters, alarms)

    # Add new Egg Rule
    def add_egg_rule(self, name, filters, alarms):
        if name in self.__egg_rules:
            raise ValueError("Unable to add Rule: Egg Rule with the name "
                             "{} already exists!".format(name))

        for filt in filters:
            if filt not in self.__egg_filters:
                raise ValueError("Unable to create Rule: No Egg Filter "
                                 "named {}!".format(filt))

        for alarm in alarms:
            if alarm not in self.__alarms:
                raise ValueError("Unable to create Rule: No Alarm "
                                 "named {}!".format(alarm))

        self.__egg_rules[name] = Rule(filters, alarms)

    # Add new Raid Rule
    def add_raid_rule(self, name, filters, alarms):
        if name in self.__raid_rules:
            raise ValueError("Unable to add Rule: Raid Rule with the name "
                             "{} already exists!".format(name))

        for filt in filters:
            if filt not in self.__raid_filters:
                raise ValueError("Unable to create Rule: No Raid Filter "
                                 "named {}!".format(filt))

        for alarm in alarms:
            if alarm not in self.__alarms:
                raise ValueError("Unable to create Rule: No Alarm "
                                 "named {}!".format(alarm))

        self.__raid_rules[name] = Rule(filters, alarms)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ MANAGER LOADING ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @staticmethod
    def load_filter_section(section, sect_name, filter_type):
        defaults = section.pop('defaults', {})
        default_dts = defaults.pop('custom_dts', {})
        filter_set = OrderedDict()
        for name, settings in section.pop('filters', {}).iteritems():
            settings = dict(defaults.items() + settings.items())
            try:
                local_dts = dict(default_dts.items()
                                 + settings.pop('custom_dts', {}).items())
                if len(local_dts) > 0:
                    settings['custom_dts'] = local_dts
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
                filters = json.load(f, object_pairs_hook=OrderedDict)
            if type(filters) is not OrderedDict:
                log.critical("Filters files must be a JSON object:"
                             " { \"monsters\":{...},... }")
                raise ValueError("Filter file did not contain a dict.")
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
            self.__mons_enabled = bool(section.pop('enabled', False))
            self.__mon_filters = self.load_filter_section(
                section, 'monsters', Filters.MonFilter)

            # Load Stops Section
            log.info("Parsing 'stops' section.")
            section = filters.pop('stops', {})
            self.__stops_enabled = bool(section.pop('enabled', False))
            self.__stop_filters = self.load_filter_section(
                section, 'stops', Filters.StopFilter)

            # Load Gyms Section
            log.info("Parsing 'gyms' section.")
            section = filters.pop('gyms', {})
            self.__gyms_enabled = bool(section.pop('enabled', False))
            self.__ignore_neutral = bool(section.pop('ignore_neutral', False))
            self.__gym_filters = self.load_filter_section(
                section, 'gyms', Filters.GymFilter)

            # Load Eggs Section
            log.info("Parsing 'eggs' section.")
            section = filters.pop('eggs', {})
            self.__eggs_enabled = bool(section.pop('enabled', False))
            self.__egg_filters = self.load_filter_section(
                section, 'eggs', Filters.EggFilter)

            # Load Raids Section
            log.info("Parsing 'raids' section.")
            section = filters.pop('raids', {})
            self.__raids_enabled = bool(section.pop('enabled', False))
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
            if type(alarm_settings) is not dict:
                log.critical("Alarms file must be an object of Alarms objects "
                             + "- { 'alarm1': {...}, ... 'alarm5': {...} }")
                sys.exit(1)
            self.__alarms = {}
            for name, alarm in alarm_settings.iteritems():
                if parse_boolean(require_and_remove_key(
                        'active', alarm, "Alarm objects in file.")) is True:
                    self.__alarms[name] = Alarms.alarm_factory(
                        alarm, max_attempts, self._google_key)
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

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HANDLE EVENTS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # Start it up
    def start(self):
        self.__process = gevent.spawn(self.run)

    def setup_in_process(self):

        # Update config
        config['DEBUG'] = self.__debug
        config['ROOT_PATH'] = os.path.abspath(
            "{}/..".format(os.path.dirname(__file__)))

        # Hush some new loggers
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)

        if config['DEBUG'] is True:
            logging.getLogger().setLevel(logging.DEBUG)

        # Conect the alarms and send the start up message
        for alarm in self.__alarms.values():
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
            except gevent.queue.Empty:
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
        raise gevent.GreenletExit()

    # Set the location of the Manager
    def set_location(self, location):
        # Regex for Lat,Lng coordinate
        prog = re.compile("^(-?\d+\.\d+)[,\s]\s*(-?\d+\.\d+?)$")
        res = prog.match(location)
        if res:  # If location is in a Lat,Lng coordinate
            self.__location = [float(res.group(1)), float(res.group(2))]
        else:
            # Check if key was provided
            if self._gmaps_service is None:
                raise ValueError("Unable to find location coordinates by name"
                                 " - no Google API key was provided.")
            # Attempt to geocode location
            location = self._gmaps_service.geocode(location)
            if location is None:
                raise ValueError("Unable to geocode coordinates from {}. "
                                 "Location will not be set.".format(location))

            self.__location = location
            log.info("Location successfully set to '{},{}'.".format(
                location[0], location[1]))

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

        # Check if previously processed and update expiration
        if self.__cache.monster_expiration(mon.enc_id) is not None:
            log.debug("{} monster was skipped because it was previously "
                      "processed.".format(mon.name))
            return
        self.__cache.monster_expiration(mon.enc_id, mon.disappear_time)

        # Check the time remaining
        seconds_left = (mon.disappear_time
                        - datetime.utcnow()).total_seconds()
        if seconds_left < self.__time_limit:
            log.debug("{} monster was skipped because only {} seconds remained"
                      "".format(mon.name, seconds_left))
            return

        # Calculate distance and direction
        if self.__location is not None:
            mon.distance = get_earth_dist(
                [mon.lat, mon.lng], self.__location, self.__units)
            mon.direction = get_cardinal_dir(
                [mon.lat, mon.lng], self.__location)

        # Check for Rules
        rules = self.__mon_rules
        if len(rules) == 0:  # If no rules, default to all
            rules = {"default": Rule(
                self.__mon_filters.keys(), self.__alarms.keys())}

        for r_name, rule in rules.iteritems():  # For all rules
            for f_name in rule.filter_names:  # Check Filters in Rules
                f = self.__mon_filters.get(f_name)
                passed = f.check_event(mon) and self.check_geofences(f, mon)
                if not passed:
                    continue  # go to next filter
                mon.custom_dts = f.custom_dts
                if self.__quiet is False:
                    log.info("{} monster notification"
                             " has been triggered in rule '{}'!"
                             "".format(mon.name, r_name))
                self._trigger_mon(mon, rule.alarm_names)
                break  # Next rule

    def _trigger_mon(self, mon, alarms):
        # Generate the DTS for the event
        dts = mon.generate_dts(self.__locale, self.__timezone, self.__units)

        # Get GMaps Triggers
        if self._gmaps_reverse_geocode:
            dts.update(self._gmaps_service.reverse_geocode(
                (mon.lat, mon.lng), self._language))
        for mode in self._gmaps_distance_matrix:
            dts.update(self._gmaps_service.distance_matrix(
                mode, (mon.lat, mon.lng), self.__location,
                self._language, self.__units))

        threads = []
        # Spawn notifications in threads so they can work in background
        for name in alarms:
            alarm = self.__alarms.get(name)
            if alarm:
                threads.append(gevent.spawn(alarm.pokemon_alert, dts))
            else:
                log.critical("Alarm '{}' not found!".format(name))

        for thread in threads:  # Wait for all alarms to finish
            thread.join()

    def process_stop(self, stop):
        # type: (Events.StopEvent) -> None
        """ Process a stop event and notify alarms if it passes. """

        # Make sure that stops are enabled
        if self.__stops_enabled is False:
            log.debug("Stop ignored: stop notifications are disabled.")
            return

        # Check for lured
        if stop.expiration is None:
            log.debug("Stop ignored: stop was not lured")
            return

        # Check if previously processed and update expiration
        if self.__cache.stop_expiration(stop.stop_id) is not None:
            log.debug("Stop {} was skipped because it was previously "
                      "processed.".format(stop.name))
            return
        self.__cache.stop_expiration(stop.stop_id, stop.expiration)

        # Check the time remaining
        seconds_left = (stop.expiration - datetime.utcnow()).total_seconds()
        if seconds_left < self.__time_limit:
            log.debug("Stop {} was skipped because only {} seconds remained"
                      "".format(stop.name, seconds_left))
            return

        # Calculate distance and direction
        if self.__location is not None:
            stop.distance = get_earth_dist(
                [stop.lat, stop.lng], self.__location, self.__units)
            stop.direction = get_cardinal_dir(
                [stop.lat, stop.lng], self.__location)

        # Check for Rules
        rules = self.__stop_rules
        if len(rules) == 0:  # If no rules, default to all
            rules = {"default": Rule(
                self.__stop_filters.keys(), self.__alarms.keys())}

        for r_name, rule in rules.iteritems():  # For all rules
            for f_name in rule.filter_names:  # Check Filters in Rules
                f = self.__stop_filters.get(f_name)
                passed = f.check_event(stop) and self.check_geofences(f, stop)
                if not passed:
                    continue  # go to next filter
                stop.custom_dts = f.custom_dts
                if self.__quiet is False:
                    log.info("{} stop notification"
                             " has been triggered in rule '{}'!"
                             "".format(stop.name, r_name))
                self._trigger_stop(stop, rule.alarm_names)
                break  # Next rule

    def _trigger_stop(self, stop, alarms):
        # Generate the DTS for the event
        dts = stop.generate_dts(self.__locale, self.__timezone, self.__units)

        # Get GMaps Triggers
        if self._gmaps_reverse_geocode:
            dts.update(self._gmaps_service.reverse_geocode(
                (stop.lat, stop.lng), self._language))
        for mode in self._gmaps_distance_matrix:
            dts.update(self._gmaps_service.distance_matrix(
                mode, (stop.lat, stop.lng), self.__location,
                self._language, self.__units))

        threads = []
        # Spawn notifications in threads so they can work in background
        for name in alarms:
            alarm = self.__alarms.get(name)
            if alarm:
                threads.append(gevent.spawn(alarm.pokestop_alert, dts))
            else:
                log.critical("Alarm '{}' not found!".format(name))

        for thread in threads:
            thread.join()

    def process_gym(self, gym):
        # type: (Events.GymEvent) -> None
        """ Process a gym event and notify alarms if it passes. """

        # Update Gym details (if they exist)
        gym.gym_name = self.__cache.gym_name(gym.gym_id, gym.gym_name)
        gym.gym_description = self.__cache.gym_desc(
            gym.gym_id, gym.gym_description)
        gym.gym_image = self.__cache.gym_image(gym.gym_id, gym.gym_image)

        # Ignore changes to neutral
        if self.__ignore_neutral and gym.new_team_id == 0:
            log.debug("%s gym update skipped: new team was neutral")
            return

        # Update Team Information
        gym.old_team_id = self.__cache.gym_team(gym.gym_id)
        self.__cache.gym_team(gym.gym_id, gym.new_team_id)

        # Check if notifications are on
        if self.__gyms_enabled is False:
            log.debug("Gym ignored: gym notifications are disabled.")
            return

        # Doesn't look like anything to me
        if gym.new_team_id == gym.old_team_id:
            log.debug("%s gym update skipped: no change detected", gym.gym_id)
            return

        # Calculate distance and direction
        if self.__location is not None:
            gym.distance = get_earth_dist(
                [gym.lat, gym.lng], self.__location, self.__units)
            gym.direction = get_cardinal_dir(
                [gym.lat, gym.lng], self.__location)

        # Check for Rules
        rules = self.__gym_rules
        if len(rules) == 0:  # If no rules, default to all
            rules = {"default": Rule(
                self.__gym_filters.keys(), self.__alarms.keys())}

        for r_name, rule in rules.iteritems():  # For all rules
            for f_name in rule.filter_names:  # Check Filters in Rules
                f = self.__gym_filters.get(f_name)
                passed = f.check_event(gym) and self.check_geofences(f, gym)
                if not passed:
                    continue  # go to next filter
                gym.custom_dts = f.custom_dts
                if self.__quiet is False:
                    log.info("{} gym notification"
                             " has been triggered in rule '{}'!"
                             "".format(gym.name, r_name))
                self._trigger_gym(gym, rule.alarm_names)
                break  # Next rule

    def _trigger_gym(self, gym, alarms):
        # Generate the DTS for the event
        dts = gym.generate_dts(self.__locale, self.__timezone, self.__units)

        # Get GMaps Triggers
        if self._gmaps_reverse_geocode:
            dts.update(self._gmaps_service.reverse_geocode(
                (gym.lat, gym.lng), self._language))
        for mode in self._gmaps_distance_matrix:
            dts.update(self._gmaps_service.distance_matrix(
                mode, (gym.lat, gym.lng), self.__location,
                self._language, self.__units))

        threads = []
        # Spawn notifications in threads so they can work in background
        for name in alarms:
            alarm = self.__alarms.get(name)
            if alarm:
                threads.append(gevent.spawn(alarm.gym_alert, dts))
            else:
                log.critical("Alarm '{}' not found!".format(name))

        for thread in threads:  # Wait for all alarms to finish
            thread.join()

    def process_egg(self, egg):
        # type: (Events.EggEvent) -> None
        """ Process a egg event and notify alarms if it passes. """

        # Update Gym details (if they exist)
        egg.gym_name = self.__cache.gym_name(egg.gym_id, egg.gym_name)
        egg.gym_description = self.__cache.gym_desc(
            egg.gym_id, egg.gym_description)
        egg.gym_image = self.__cache.gym_image(egg.gym_id, egg.gym_image)

        # Update Team if Unknown
        if Unknown.is_(egg.current_team_id):
            egg.current_team_id = self.__cache.gym_team(egg.gym_id)

        # Make sure that eggs are enabled
        if self.__eggs_enabled is False:
            log.debug("Egg ignored: egg notifications are disabled.")
            return

        # Skip if previously processed
        if self.__cache.egg_expiration(egg.gym_id) is not None:
            log.debug("Egg {} was skipped because it was previously "
                      "processed.".format(egg.name))
            return
        self.__cache.egg_expiration(egg.gym_id, egg.hatch_time)

        # Check the time remaining
        seconds_left = (egg.hatch_time - datetime.utcnow()).total_seconds()
        if seconds_left < self.__time_limit:
            log.debug("Egg {} was skipped because only {} seconds remained"
                      "".format(egg.name, seconds_left))
            return

        # Calculate distance and direction
        if self.__location is not None:
            egg.distance = get_earth_dist(
                [egg.lat, egg.lng], self.__location, self.__units)
            egg.direction = get_cardinal_dir(
                [egg.lat, egg.lng], self.__location)

        # Check for Rules
        rules = self.__egg_rules
        if len(rules) == 0:  # If no rules, default to all
            rules = {"default": Rule(
                self.__egg_filters.keys(), self.__alarms.keys())}

        for r_name, rule in rules.iteritems():  # For all rules
            for f_name in rule.filter_names:  # Check Filters in Rules
                f = self.__egg_filters.get(f_name)
                passed = f.check_event(egg) and self.check_geofences(f, egg)
                if not passed:
                    continue  # go to next filter
                egg.custom_dts = f.custom_dts
                if self.__quiet is False:
                    log.info("{} egg notification"
                             " has been triggered in rule '{}'!"
                             "".format(egg.name, r_name))
                self._trigger_egg(egg, rule.alarm_names)
                break  # Next rule

    def _trigger_egg(self, egg, alarms):
        # Generate the DTS for the event
        dts = egg.generate_dts(self.__locale, self.__timezone, self.__units)

        # Get GMaps Triggers
        if self._gmaps_reverse_geocode:
            dts.update(self._gmaps_service.reverse_geocode(
                (egg.lat, egg.lng), self._language))
        for mode in self._gmaps_distance_matrix:
            dts.update(self._gmaps_service.distance_matrix(
                mode, (egg.lat, egg.lng), self.__location,
                self._language, self.__units))

        threads = []
        # Spawn notifications in threads so they can work in background
        for name in alarms:
            alarm = self.__alarms.get(name)
            if alarm:
                threads.append(gevent.spawn(alarm.raid_egg_alert, dts))
            else:
                log.critical("Alarm '{}' not found!".format(name))

        for thread in threads:  # Wait for all alarms to finish
            thread.join()

    def process_raid(self, raid):
        # type: (Events.RaidEvent) -> None
        """ Process a raid event and notify alarms if it passes. """

        # Update Gym details (if they exist)
        raid.gym_name = self.__cache.gym_name(raid.gym_id, raid.gym_name)
        raid.gym_description = self.__cache.gym_desc(
            raid.gym_id, raid.gym_description)
        raid.gym_image = self.__cache.gym_image(raid.gym_id, raid.gym_image)

        # Update Team if Unknown
        if Unknown.is_(raid.current_team_id):
            raid.current_team_id = self.__cache.gym_team(raid.gym_id)

        # Make sure that raids are enabled
        if self.__raids_enabled is False:
            log.debug("Raid ignored: raid notifications are disabled.")
            return

        # Skip if previously processed
        if self.__cache.raid_expiration(raid.gym_id) is not None:
            log.debug("Raid {} was skipped because it was previously "
                      "processed.".format(raid.name))
            return
        self.__cache.raid_expiration(raid.gym_id, raid.raid_end)

        # Check the time remaining
        seconds_left = (raid.raid_end - datetime.utcnow()).total_seconds()
        if seconds_left < self.__time_limit:
            log.debug("Raid {} was skipped because only {} seconds remained"
                      "".format(raid.name, seconds_left))
            return

        # Calculate distance and direction
        if self.__location is not None:
            raid.distance = get_earth_dist(
                [raid.lat, raid.lng], self.__location, self.__units)
            raid.direction = get_cardinal_dir(
                [raid.lat, raid.lng], self.__location)

        # Check for Rules
        rules = self.__raid_rules
        if len(rules) == 0:  # If no rules, default to all
            rules = {"default": Rule(
                self.__raid_filters.keys(), self.__alarms.keys())}

        for r_name, rule in rules.iteritems():  # For all rules
            for f_name in rule.filter_names:  # Check Filters in Rules
                f = self.__raid_filters.get(f_name)
                passed = f.check_event(raid) and self.check_geofences(f, raid)
                if not passed:
                    continue  # go to next filter
                raid.custom_dts = f.custom_dts
                if self.__quiet is False:
                    log.info("{} raid notification"
                             " has been triggered in rule '{}'!"
                             "".format(raid.name, r_name))
                self._trigger_raid(raid, rule.alarm_names)
                break  # Next rule

    def _trigger_raid(self, raid, alarms):
        # Generate the DTS for the event
        dts = raid.generate_dts(self.__locale, self.__timezone, self.__units)

        # Get GMaps Triggers
        if self._gmaps_reverse_geocode:
            dts.update(self._gmaps_service.reverse_geocode(
                (raid.lat, raid.lng), self._language))
        for mode in self._gmaps_distance_matrix:
            dts.update(self._gmaps_service.distance_matrix(
                mode, (raid.lat, raid.lng), self.__location,
                self._language, self.__units))

        threads = []
        # Spawn notifications in threads so they can work in background
        for name in alarms:
            alarm = self.__alarms.get(name)
            if alarm:
                threads.append(gevent.spawn(alarm.raid_alert, dts))
            else:
                log.critical("Alarm '{}' not found!".format(name))

        for thread in threads:  # Wait for all alarms to finish
            thread.join()

    # Check to see if a notification is within the given range
    def check_geofences(self, f, e):
        """ Returns true if the event passes the filter's geofences. """
        if self.geofences is None or f.geofences is None:  # No geofences set
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

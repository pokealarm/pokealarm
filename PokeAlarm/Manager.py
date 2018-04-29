# Standard Library Imports
import logging
import logging.handlers
import os
import re
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
from PokeAlarm.Utilities.Logging import ContextFilter, setup_file_handler
from PokeAlarm.Utilities.GenUtils import parse_bool
from Utils import (get_earth_dist, get_path, get_cardinal_dir)
from . import config
Rule = namedtuple('Rule', ['filter_names', 'alarm_names'])


class Manager(object):
    def __init__(self, name, google_key, locale, units, timezone, time_limit,
                 max_attempts, location, cache_type, geofence_file, debug):
        # Set the name of the Manager
        self.name = str(name).lower()
        self._log = self._create_logger(self.name)
        self._rule_log = self.get_child_logger('rules')

        self.__debug = debug

        # Get the Google Maps AP# TODO: Improve error checking
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
            self._log.warning(
                "NO LOCATION SET - this may cause issues "
                "with distance related DTS.")

        # Create cache
        self.__cache = cache_factory(self, cache_type)

        # Load and Setup the Pokemon Filters
        self._mons_enabled, self._mon_filters = False, OrderedDict()
        self._stops_enabled, self._stop_filters = False, OrderedDict()
        self._gyms_enabled, self._gym_filters = False, OrderedDict()
        self._ignore_neutral = False
        self._eggs_enabled, self._egg_filters = False, OrderedDict()
        self._raids_enabled, self._raid_filters = False, OrderedDict()
        self._weather_enabled, self._weather_filters = False, OrderedDict()

        # Create the Geofences to filter with from given file
        self.geofences = None
        if str(geofence_file).lower() != 'none':
            self.geofences = load_geofence_file(get_path(geofence_file))
        # Create the alarms to send notifications out with
        self._alarms = {}
        self._max_attempts = int(max_attempts)  # TODO: Move to alarm level

        # Initialize Rules
        self.__mon_rules = {}
        self.__stop_rules = {}
        self.__gym_rules = {}
        self.__egg_rules = {}
        self.__raid_rules = {}
        self.__weather_rules = {}

        # Initialize the queue and start the process
        self.__queue = Queue()
        self.__event = Event()
        self.__process = None

    # ~~~~~~~~~~~~~~~~~~~~~~~ MAIN PROCESS CONTROL ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # Update the object into the queue
    def update(self, obj):
        self.__queue.put(obj)

    # Get the name of this Manager
    def get_name(self):
        return self.name

    # Tell the process to finish up and go home
    def stop(self):
        self._log.info(
            "Manager {} shutting down... {} items in queue."
            "".format(self.name, self.__queue.qsize()))
        self.__event.set()

    def join(self):
        self.__process.join(timeout=20)
        if not self.__process.ready():
            self._log.warning("Manager {} could not be stopped in time! "
                              "Forcing process to stop.".format(self.name))
            self.__process.kill(timeout=2, block=True)  # Force stop
        else:
            self._log.info(
                "Manager {} successfully stopped!".format(self.name))

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

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ LOGGING ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @staticmethod
    def _create_logger(mgr_name):
        """ Internal method for initializing manager loggers. """
        # Create a Filter to pass on manager name
        log = logging.getLogger('pokealarm.{}'.format(mgr_name))
        return log

    def get_child_logger(self, name):
        """ Get a child logger of this manager. """
        logger = self._log.getChild(name)
        logger.addFilter(ContextFilter())
        return logger

    def set_log_level(self, log_level):
        if log_level == 1:
            self._log.setLevel(logging.WARNING)
        elif log_level == 2:
            self._log.setLevel(logging.INFO)
            self._log.getChild("cache").setLevel(logging.WARNING)
            self._log.getChild("filters").setLevel(logging.WARNING)
            self._log.getChild("alarms").setLevel(logging.WARNING)
        elif log_level == 3:
            self._log.setLevel(logging.INFO)
            self._log.getChild("cache").setLevel(logging.INFO)
            self._log.getChild("filters").setLevel(logging.WARNING)
            self._log.getChild("alarms").setLevel(logging.WARNING)
        elif log_level == 4:
            self._log.setLevel(logging.INFO)
            self._log.getChild("cache").setLevel(logging.INFO)
            self._log.getChild("filters").setLevel(logging.INFO)
            self._log.getChild("alarms").setLevel(logging.INFO)
        elif log_level == 5:
            self._log.setLevel(logging.DEBUG)
            self._log.getChild("cache").setLevel(logging.DEBUG)
            self._log.getChild("filters").setLevel(logging.DEBUG)
            self._log.getChild("alarms").setLevel(logging.DEBUG)
        else:
            raise ValueError("Unable to set verbosity, must be an "
                             "integer between 1 and 5.")
        self._log.debug("Verbosity set to %s", log_level)

    def add_file_logger(self, path, max_size_mb, ct):
        setup_file_handler(self._log, path, max_size_mb, ct)
        self._log.debug("Added new file logger to %s", path)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ FILTERS API ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # Enable/Disable Monster notifications
    def set_monsters_enabled(self, boolean):
        self._mons_enabled = parse_bool(boolean)
        self._log.debug("Monster notifications %s",
                        "enabled" if self._mons_enabled else "disabled")

    # Add new Monster Filter
    def add_monster_filter(self, name, settings):
        if name in self._mon_filters:
            raise ValueError("Unable to add Monster Filter: Filter with the "
                             "name {} already exists!".format(name))
        f = Filters.MonFilter(self, name, settings)
        self._mon_filters[name] = f
        self._log.debug("Monster filter '%s' set: %s", name, f)

    # Enable/Disable Stops notifications
    def set_stops_enabled(self, boolean):
        self._stops_enabled = parse_bool(boolean)
        self._log.debug("Stops notifications %s!",
                        "enabled" if self._stops_enabled else "disabled")

    # Add new Stop Filter
    def add_stop_filter(self, name, settings):
        if name in self._stop_filters:
            raise ValueError("Unable to add Stop Filter: Filter with the "
                             "name {} already exists!".format(name))
        f = Filters.StopFilter(self, name, settings)
        self._stop_filters[name] = f
        self._log.debug("Stop filter '%s' set: %s", name, f)

    # Enable/Disable Gym notifications
    def set_gyms_enabled(self, boolean):
        self._gyms_enabled = parse_bool(boolean)
        self._log.debug("Gyms notifications %s!",
                        "enabled" if self._gyms_enabled else "disabled")

    # Enable/Disable Stops notifications
    def set_ignore_neutral(self, boolean):
        self._ignore_neutral = parse_bool(boolean)
        self._log.debug("Ignore neutral set to %s!", self._ignore_neutral)

    # Add new Gym Filter
    def add_gym_filter(self, name, settings):
        if name in self._gym_filters:
            raise ValueError("Unable to add Gym Filter: Filter with the "
                             "name {} already exists!".format(name))
        f = Filters.GymFilter(self, name, settings)
        self._gym_filters[name] = f
        self._log.debug("Gym filter '%s' set: %s", name, f)

    # Enable/Disable Egg notifications
    def set_eggs_enabled(self, boolean):
        self._eggs_enabled = parse_bool(boolean)
        self._log.debug("Egg notifications %s!",
                        "enabled" if self._eggs_enabled else "disabled")

    # Add new Egg Filter
    def add_egg_filter(self, name, settings):
        if name in self._egg_filters:
            raise ValueError("Unable to add Egg Filter: Filter with the "
                             "name {} already exists!".format(name))
        f = Filters.EggFilter(self, name, settings)
        self._egg_filters[name] = f
        self._log.debug("Egg filter '%s' set: %s", name, f)

    # Enable/Disable Stops notifications
    def set_raids_enabled(self, boolean):
        self._raids_enabled = parse_bool(boolean)
        self._log.debug("Raid notifications %s!",
                        "enabled" if self._raids_enabled else "disabled")

    # Add new Raid Filter
    def add_raid_filter(self, name, settings):
        if name in self._raid_filters:
            raise ValueError("Unable to add Raid Filter: Filter with the "
                             "name {} already exists!".format(name))
        f = Filters.RaidFilter(self, name, settings)
        self._raid_filters[name] = f
        self._log.debug("Raid filter '%s' set: %s", name, f)

    # Enable/Disable Weather notifications
    def set_weather_enabled(self, boolean):
        self._weather_enabled = parse_bool(boolean)
        self._log.debug("Weather notifications %s!",
                        "enabled" if self._weather_enabled else "disabled")

    # Add new Weather Filter
    def add_weather_filter(self, name, settings):
        if name in self._weather_filters:
            raise ValueError("Unable to add Weather Filter: Filter with the "
                             "name {} already exists!".format(name))
        f = Filters.WeatherFilter(self, name, settings)
        self._weather_filters[name] = f
        self._log.debug("Weather filter '%s' set: %s", name, f)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ALARMS API ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def add_alarm(self, name, settings):
        if name in self._alarms:
            raise ValueError("Unable to add new Alarm: Alarm with the name "
                             "{} already exists!".format(name))
        alarm = Alarms.alarm_factory(
            self, settings, self._max_attempts, self._google_key)
        self._alarms[name] = alarm

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ RULES API ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # Add new Monster Rule
    def add_monster_rule(self, name, filters, alarms):
        if name in self.__mon_rules:
            raise ValueError("Unable to add Rule: Monster Rule with the name "
                             "{} already exists!".format(name))

        for filt in filters:
            if filt not in self._mon_filters:
                raise ValueError("Unable to create Rule: No Monster Filter "
                                 "named {}!".format(filt))

        for alarm in alarms:
            if alarm not in self._alarms:
                raise ValueError("Unable to create Rule: No Alarm "
                                 "named {}!".format(alarm))

        self.__mon_rules[name] = Rule(filters, alarms)

    # Add new Stop Rule
    def add_stop_rule(self, name, filters, alarms):
        if name in self.__stop_rules:
            raise ValueError("Unable to add Rule: Stop Rule with the name "
                             "{} already exists!".format(name))

        for filt in filters:
            if filt not in self._stop_filters:
                raise ValueError("Unable to create Rule: No Stop Filter "
                                 "named {}!".format(filt))

        for alarm in alarms:
            if alarm not in self._alarms:
                raise ValueError("Unable to create Rule: No Alarm "
                                 "named {}!".format(alarm))

        self.__stop_rules[name] = Rule(filters, alarms)

    # Add new Gym Rule
    def add_gym_rule(self, name, filters, alarms):
        if name in self.__gym_rules:
            raise ValueError("Unable to add Rule: Gym Rule with the name "
                             "{} already exists!".format(name))

        for filt in filters:
            if filt not in self._gym_filters:
                raise ValueError("Unable to create Rule: No Gym Filter "
                                 "named {}!".format(filt))

        for alarm in alarms:
            if alarm not in self._alarms:
                raise ValueError("Unable to create Rule: No Alarm "
                                 "named {}!".format(alarm))

        self.__gym_rules[name] = Rule(filters, alarms)

    # Add new Egg Rule
    def add_egg_rule(self, name, filters, alarms):
        if name in self.__egg_rules:
            raise ValueError("Unable to add Rule: Egg Rule with the name "
                             "{} already exists!".format(name))

        for filt in filters:
            if filt not in self._egg_filters:
                raise ValueError("Unable to create Rule: No Egg Filter "
                                 "named {}!".format(filt))

        for alarm in alarms:
            if alarm not in self._alarms:
                raise ValueError("Unable to create Rule: No Alarm "
                                 "named {}!".format(alarm))

        self.__egg_rules[name] = Rule(filters, alarms)

    # Add new Raid Rule
    def add_raid_rule(self, name, filters, alarms):
        if name in self.__raid_rules:
            raise ValueError("Unable to add Rule: Raid Rule with the name "
                             "{} already exists!".format(name))

        for filt in filters:
            if filt not in self._raid_filters:
                raise ValueError("Unable to create Rule: No Raid Filter "
                                 "named {}!".format(filt))

        for alarm in alarms:
            if alarm not in self._alarms:
                raise ValueError("Unable to create Rule: No Alarm "
                                 "named {}!".format(alarm))

        self.__raid_rules[name] = Rule(filters, alarms)

    # Add new Weather Rule
    def add_weather_rule(self, name, filters, alarms):
        if name in self.__weather_rules:
            raise ValueError("Unable to add Rule: Weather Rule with the name "
                             "{} already exists!".format(name))

        for filt in filters:
            if filt not in self._weather_filters:
                raise ValueError("Unable to create Rule: No Weather Filter "
                                 "named {}!".format(filt))

        for alarm in alarms:
            if alarm not in self._alarms:
                raise ValueError("Unable to create Rule: No Alarm "
                                 "named {}!".format(alarm))

        self.__weather_rules[name] = Rule(filters, alarms)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ MANAGER LOADING ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
        for alarm in self._alarms.values():
            alarm.connect()
            alarm.startup_message()

    # Main event handler loop
    def run(self):
        self.setup_in_process()
        last_clean = datetime.utcnow()
        while True:  # Run forever and ever

            # Clean out visited every 5 minutes
            if datetime.utcnow() - last_clean > timedelta(minutes=5):
                self._log.debug("Cleaning cache...")
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
                self._log.debug("Processing event: %s", event.id)
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
                elif kind == Events.WeatherEvent:
                    self.process_weather(event)
                else:
                    self._log.error(
                        "!!! Manager does not support {} events!".format(kind))
                self._log.debug("Finished event: %s", event.id)
            except Exception as e:
                self._log.error("Encountered error during processing: "
                                "{}: {}".format(type(e).__name__, e))
                self._log.error("Stack trace: \n {}"
                                "".format(traceback.format_exc()))
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
            self._log.info("Location successfully set to '{},{}'.".format(
                location[0], location[1]))

    def _check_filters(self, event, filter_set, filter_names):
        """ Function for checking if an event passes any filters. """
        for name in filter_names:
            f = filter_set.get(name)
            # Filter should always exist, but sanity check anyway
            if f:
                # If the Event passes, return True
                if f.check_event(event) and self.check_geofences(f, event):
                    event.custom_dts = f.custom_dts
                    return True
            else:
                self._log.critical("ERROR: No filter named %s found!", name)
        return False

    def _notify_alarms(self, event, alarm_names, func_name):
        """ Function for triggering notifications to alarms. """
        # Generate the DTS for the event
        dts = event.generate_dts(self.__locale, self.__timezone, self.__units)

        # Get GMaps Triggers
        if self._gmaps_reverse_geocode:
            dts.update(self._gmaps_service.reverse_geocode(
                (event.lat, event.lng), self._language))
        for mode in self._gmaps_distance_matrix:
            dts.update(self._gmaps_service.distance_matrix(
                mode, (event.lat, event.lng), self.__location,
                self._language, self.__units))

        # Spawn notifications in threads so they can work asynchronously
        threads = []
        for name in alarm_names:
            alarm = self._alarms.get(name)
            if not alarm:
                self._log.critical("ERROR: No alarm named %s found!", name)
                continue
            func = getattr(alarm, func_name)
            threads.append(gevent.spawn(func, dts))

        for thread in threads:  # Wait for all alarms to finish
            thread.join()

    # Process new Monster data and decide if a notification needs to be sent
    def process_monster(self, mon):
        # type: (Events.MonEvent) -> None
        """ Process a monster event and notify alarms if it passes. """

        # Make sure that monsters are enabled
        if self._mons_enabled is False:
            self._log.debug("Monster ignored: monster notifications "
                            "are disabled.")
            return

        # Set the name for this event so we can log rejects better
        mon.name = self.__locale.get_pokemon_name(mon.monster_id)

        # Check if previously processed and update expiration
        if self.__cache.monster_expiration(mon.enc_id) is not None:
            self._log.debug("{} monster was skipped because it was "
                            "previously processed.".format(mon.name))
            return
        self.__cache.monster_expiration(mon.enc_id, mon.disappear_time)

        # Check the time remaining
        seconds_left = (mon.disappear_time
                        - datetime.utcnow()).total_seconds()
        if seconds_left < self.__time_limit:
            self._log.debug("{} monster was skipped because only {} seconds "
                            "remained".format(mon.name, seconds_left))
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
            rules = {
                "default": Rule(self._mon_filters.keys(), self._alarms.keys())}

        rule_ct, alarm_ct = 0, 0
        for r_name, rule in rules.iteritems():  # For all rules
            passed = self._check_filters(
                mon, self._mon_filters, rule.filter_names)
            if passed:
                rule_ct += 1
                alarm_ct += len(rule.alarm_names)
                self._notify_alarms(
                    mon, rule.alarm_names, 'pokemon_alert')

        if rule_ct > 0:
            self._rule_log.info(
                'Monster %s passed %s rule(s) and triggered %s alarm(s).',
                mon.name, rule_ct, alarm_ct)
        else:
            self._rule_log.info('Monster %s rejected by all rules.', mon.name)

    def process_stop(self, stop):
        # type: (Events.StopEvent) -> None
        """ Process a stop event and notify alarms if it passes. """

        # Make sure that stops are enabled
        if self._stops_enabled is False:
            self._log.debug("Stop ignored: stop notifications are disabled.")
            return

        # Check for lured
        if stop.expiration is None:
            self._log.debug("Stop ignored: stop was not lured")
            return

        # Check if previously processed and update expiration
        if self.__cache.stop_expiration(stop.stop_id) is not None:
            self._log.debug("Stop {} was skipped because it was "
                            "previously processed.".format(stop.name))
            return
        self.__cache.stop_expiration(stop.stop_id, stop.expiration)

        # Check the time remaining
        seconds_left = (stop.expiration - datetime.utcnow()).total_seconds()
        if seconds_left < self.__time_limit:
            self._log.debug("Stop {} was skipped because only {} seconds "
                            "remained".format(stop.name, seconds_left))
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
                self._stop_filters.keys(), self._alarms.keys())}

        rule_ct, alarm_ct = 0, 0
        for r_name, rule in rules.iteritems():  # For all rules
            passed = self._check_filters(
                stop, self._stop_filters, rule.filter_names)
            if passed:
                rule_ct += 1
                alarm_ct += len(rule.alarm_names)
                self._notify_alarms(
                    stop, rule.alarm_names, 'pokestop_alert')

        if rule_ct > 0:
            self._rule_log.info(
                'Stop %s passed %s rule(s) and triggered %s alarm(s).',
                stop.name, rule_ct, alarm_ct)
        else:
            self._rule_log.info('Stop %s rejected by all rules.', stop.name)

    def process_gym(self, gym):
        # type: (Events.GymEvent) -> None
        """ Process a gym event and notify alarms if it passes. """

        # Update Gym details (if they exist)
        gym.gym_name = self.__cache.gym_name(gym.gym_id, gym.gym_name)
        gym.gym_description = self.__cache.gym_desc(
            gym.gym_id, gym.gym_description)
        gym.gym_image = self.__cache.gym_image(gym.gym_id, gym.gym_image)

        # Ignore changes to neutral
        if self._ignore_neutral and gym.new_team_id == 0:
            self._log.debug("%s gym update skipped: new team was neutral")
            return

        # Update Team Information
        gym.old_team_id = self.__cache.gym_team(gym.gym_id)
        self.__cache.gym_team(gym.gym_id, gym.new_team_id)

        # Check if notifications are on
        if self._gyms_enabled is False:
            self._log.debug("Gym ignored: gym notifications are disabled.")
            return

        # Doesn't look like anything to me
        if gym.new_team_id == gym.old_team_id:
            self._log.debug(
                "%s gym update skipped: no change detected", gym.gym_id)
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
                self._gym_filters.keys(), self._alarms.keys())}

        rule_ct, alarm_ct = 0, 0
        for r_name, rule in rules.iteritems():  # For all rules
            passed = self._check_filters(
                gym, self._gym_filters, rule.filter_names)
            if passed:
                rule_ct += 1
                alarm_ct += len(rule.alarm_names)
                self._notify_alarms(
                    gym, rule.alarm_names, 'gym_alert')

        if rule_ct > 0:
            self._rule_log.info(
                'Gym %s passed %s rule(s) and triggered %s alarm(s).',
                gym.name, rule_ct, alarm_ct)
        else:
            self._rule_log.info('Gym %s rejected by all rules.', gym.name)

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
        if self._eggs_enabled is False:
            self._log.debug("Egg ignored: egg notifications are disabled.")
            return

        # Skip if previously processed
        if self.__cache.egg_expiration(egg.gym_id) is not None:
            self._log.debug("Egg {} was skipped because it was "
                            "previously processed.".format(egg.name))
            return
        self.__cache.egg_expiration(egg.gym_id, egg.hatch_time)

        # Check the time remaining
        seconds_left = (egg.hatch_time - datetime.utcnow()).total_seconds()
        if seconds_left < self.__time_limit:
            self._log.debug("Egg {} was skipped because only {} seconds "
                            "remained".format(egg.name, seconds_left))
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
            rules = {
                "default": Rule(self._egg_filters.keys(), self._alarms.keys())}

        rule_ct, alarm_ct = 0, 0
        for r_name, rule in rules.iteritems():  # For all rules
            passed = self._check_filters(
                egg, self._egg_filters, rule.filter_names)
            if passed:
                rule_ct += 1
                alarm_ct += len(rule.alarm_names)
                self._notify_alarms(
                    egg, rule.alarm_names, 'raid_egg_alert')

        if rule_ct > 0:
            self._rule_log.info(
                'Egg %s passed %s rule(s) and triggered %s alarm(s).',
                egg.name, rule_ct, alarm_ct)
        else:
            self._rule_log.info('Egg %s rejected by all rules.', egg.name)

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
        if self._raids_enabled is False:
            self._log.debug("Raid ignored: raid notifications are disabled.")
            return

        # Skip if previously processed
        if self.__cache.raid_expiration(raid.gym_id) is not None:
            self._log.debug("Raid {} was skipped because it was "
                            "previously processed.".format(raid.name))
            return
        self.__cache.raid_expiration(raid.gym_id, raid.raid_end)

        # Check the time remaining
        seconds_left = (raid.raid_end - datetime.utcnow()).total_seconds()
        if seconds_left < self.__time_limit:
            self._log.debug("Raid {} was skipped because only {} seconds "
                            "remained".format(raid.name, seconds_left))
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
                self._raid_filters.keys(), self._alarms.keys())}

        rule_ct, alarm_ct = 0, 0
        for r_name, rule in rules.iteritems():  # For all rules
            passed = self._check_filters(
                raid, self._raid_filters, rule.filter_names)
            if passed:
                rule_ct += 1
                alarm_ct += len(rule.alarm_names)
                self._notify_alarms(
                    raid, rule.alarm_names, 'raid_alert')

        if rule_ct > 0:
            self._rule_log.info(
                'Raid %s passed %s rule(s) and triggered %s alarm(s).',
                raid.name, rule_ct, alarm_ct)
        else:
            self._rule_log.info('Raid %s rejected by all rules.', raid.name)

    def process_weather(self, weather):
        # type: (Events.WeatherEvent) -> None
        """ Process a weather event and notify alarms if it passes. """

        # Set the name for this event so we can log rejects better
        weather.name = self.__locale.get_weather_name(weather.s2_cell_id)

        # Make sure that weather changes are enabled
        if self._weather_enabled is False:
            self._log.debug("Weather ignored: weather change "
                            "notifications are disabled.")
            return

        # Calculate distance and direction
        if self.__location is not None:
            weather.distance = get_earth_dist(
                [weather.lat, weather.lng], self.__location, self.__units)
            weather.direction = get_cardinal_dir(
                [weather.lat, weather.lng], self.__location)

        # Store copy of cache info
        cache_weather_id = self.__cache.cell_weather_id(weather.s2_cell_id)
        cache_day_or_night_id = self.__cache.day_or_night_id(
            weather.s2_cell_id)
        cache_severity_id = self.__cache.severity_id(weather.s2_cell_id)

        # Update cache info
        self.__cache.cell_weather_id(weather.s2_cell_id,
                                     weather.weather_id)
        self.__cache.day_or_night_id(
            weather.s2_cell_id, weather.day_or_night_id)
        self.__cache.severity_id(weather.s2_cell_id, weather.severity_id)

        # Check and see if the weather hasn't changed and ignore
        if weather.weather_id == cache_weather_id and \
                weather.day_or_night_id == cache_day_or_night_id and \
                weather.severity_id == cache_severity_id:
            self._log.debug(
                "weather of %s, alert of %s, and day or night of %s skipped: "
                "no change detected",
                weather.weather_id, weather.severity_id,
                weather.day_or_night_id)
            return

        # Check for Rules
        rules = self.__weather_rules
        if len(rules) == 0:  # If no rules, default to all
            rules = {"default": Rule(
                self._weather_filters.keys(), self._alarms.keys())}

        rule_ct, alarm_ct = 0, 0
        for r_name, rule in rules.iteritems():  # For all rules
            passed = self._check_filters(
                weather, self._weather_filters, rule.filter_names)
            if passed:
                rule_ct += 1
                alarm_ct += len(rule.alarm_names)
                self._notify_alarms(
                    weather, rule.alarm_names, 'weather_alert')

        if rule_ct > 0:
            self._rule_log.info(
                'Weather %s passed %s rule(s) and triggered %s alarm(s).',
                weather.name, rule_ct, alarm_ct)
        else:
            self._rule_log.info(
                'Weather %s rejected by all rules.', weather.name)

    # Check to see if a notification is within the given range
    # TODO: Move this into filters and add unit tests
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
                self._log.error("Cannot check geofence %s: "
                                "does not exist!", name)
            elif gf.contains(e.lat, e.lng):  # e in gf
                self._log.debug("{} is in geofence {}!".format(
                    e.name, gf.get_name()))
                e.geofence = name  # Set the geofence for dts
                return True
            else:  # e not in gf
                self._log.debug("%s not in %s.", e.name, name)
        self._log.debug("%s rejected from filter by geofences.", e.name)
        return False

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

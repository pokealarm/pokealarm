# Standard Library Imports
from datetime import datetime, timedelta
import gevent
import logging
import json
import multiprocessing
import traceback
import os
import re
# 3rd Party Imports
import gipc
import googlemaps
# Local Imports
from . import config
from Structures import Geofence
from Utils import contains_arg, get_cardinal_dir, get_dist_as_str, get_earth_dist, get_path, get_pkmn_id, get_team_id,\
    get_time_as_str, parse_boolean

log = logging.getLogger('Manager')


class Manager(object):

    def __init__(self, name, google_key, filters, geofences, alarms, location, locale, units, time_limit, timezone):

        # Set the name of the Manager
        self.__name = str(name).lower()
        log.info("Setting up {} process.".format(self.__name))

        # Set up the Google API
        self.__google_key = google_key
        self.__gmaps_client = googlemaps.Client(key=self.__google_key) if self.__google_key is not None else None

        # Set up the rules on filtering notifications from given file
        self.__pokemon_filter = None
        self.__pokemon_hist = {}
        self.__pokestop_filter = None
        self.__pokestop_hist = {}
        self.__gym_filter = None
        self.__gym_hist = {}
        self.create_filters(get_path(filters))

        # Create the Geofences to filter with from given file
        self.__geofences = []
        self.__geofences_config = geofences

        # Create the alarms to send notifications out with
        self.__api_req = {'REVERSE_LOCATION': False, 'WALK_DIST': False, 'BIKE_DIST': False, 'DRIVE_DIST': False}
        self.__alarms = []
        self.__alarms_file = get_path(alarms)

        # Set the location
        self.__latlng = self.get_lat_lng_by_name(location) if location is not None else []

        # Set the locale to use for names and moves
        self.__pokemon_name, self.__move_name, self.__team_name = {}, {}, {}
        self.__locale = locale
        self.update_locales()

        # Set the units to be used
        self.__units = units

        # Set the minimum time_limit to send a notification (for pkmn/lures)
        self.__time_limit = time_limit

        # Set the timezone to use
        self.__timezone = timezone if str(timezone).lower() != 'none' else None

        # Initialize the queue and start the process
        self.__config = config
        self.__threads = []  # Notification threads
        self.__queue = multiprocessing.Queue()
        self.__process = gipc.start_process(target=self.run, args=(), name=self.__name)

    ############################################## CALLED BY MAIN PROCESS ##############################################

    # Update the object into the queue
    def update(self, obj):
        self.__queue.put(obj)

    def get_name(self):
        return self.__name

    ####################################################################################################################
    ################################################## HANDLE EVENTS  ##################################################

    # Set up some variables that don't get moved into the new process correctly
    def intialize_process(self):
        # Update config
        config.update(**self.__config)
        config['TIMEZONE'] = self.__timezone
        config['API_KEY'] = self.__google_key
        config['UNITS'] = self.__units

        # Hush some new loggers
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)

        if config['DEBUG'] is True:
            logging.getLogger().setLevel(logging.DEBUG)

        # Make the Alarms
        self.create_alarms(self.__alarms_file)
        if self.__geofences_config is not None:
            self.create_geofences(get_path(self.__geofences_config))

    def run(self):
        self.intialize_process()

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
                    self.handle_pokemon(obj)
                elif kind == "pokestop":
                    self.handle_pokestop(obj)
                elif kind == "gym":
                    self.handle_gym(obj)
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

    def handle_pokemon(self, pkmn):
        # Quick check for enabled
        if self.__pokemon_filter['enabled'] is False:
            log.debug("Pokemon ignored: notifications are disabled.")
            return

        id_ = pkmn['id']
        pkmn_id = pkmn['pkmn_id']
        name = self.__pokemon_name[pkmn_id]

        # Check for previously processed
        if id_ in self.__pokemon_hist:
            if config['QUIET'] is False:
                log.debug("{} was skipped because it was previously processed.".format(name))
            return
        self.__pokemon_hist[id_] = pkmn['disappear_time']

        # Check that the filter is set
        if pkmn_id not in self.__pokemon_filter:
            if config['QUIET'] is False:
                log.info("{} ignored: filter was not set".format(name))
                return

        # Check the time remaining
        seconds_left = (pkmn['disappear_time'] - datetime.utcnow()).total_seconds()
        if seconds_left < self.__time_limit:
            if config['QUIET'] is False:
                log.info("{} ignored: {} seconds remaining.".format(name, seconds_left))
            return

        filt = self.__pokemon_filter[pkmn_id]

        # Check the distance from the set location
        lat, lng = pkmn['lat'], pkmn['lng']
        dist = get_earth_dist([lat, lng], self.__latlng)
        if dist != 'unkn':
            if dist < filt['min_dist'] or filt['max_dist'] < dist:
                if config['QUIET'] is False:
                    log.info("{} ignored: distance ({:.2f}) was not in range {:.2f} to {:.2f}.".format(
                        name, dist, filt['min_dist'], filt['max_dist']))
                return
        else:
            log.debug("Pokemon dist was not checked because no location was set.")

        # Check the IV's of the Pokemon
        iv = pkmn['iv']
        if iv != 'unkn':
            if iv < filt['min_iv'] or filt['max_iv'] < iv:
                if config['QUIET'] is False:
                    log.info("{} ignored: IVs ({:.2f}) not in range {:.2f} to {:.2f}.".format(
                        name, iv, filt['min_iv'], filt['max_iv']))
                return
            pkmn['iv'] = "{:.1f}".format(iv)
        else:
            log.debug("Pokemon IV's were not checked because they are unknown.")

        # Check the moves of the Pokemon
        move1 = self.__move_name.get(pkmn['move_1_id'], 'unknown')
        move2 = self.__move_name.get(pkmn['move_2_id'], 'unknown')
        # TODO: Move damage
        if move1 != 'unknown' and move2 != 'unknown':
            move_1_f, move_2_f = filt['move_1'], filt['move_2']
            if move_1_f is not None and move_1_f.find(move1) == -1:
                if config['QUIET'] is False:
                    log.info("{} ignored: Move 1 was incorrect.".format(name))
                return
            if move_2_f is not None and move_2_f.find(move2) == -1:
                if config['QUIET'] is False:
                    log.info("{} ignored: Move 2 was incorrect.".format(name))
                return
        else:
            log.debug("Pokemon moves were not checked because they are unknown.")

        # Check if in geofences
        if len(self.__geofences) > 0:
            inside = False
            for gf in self.__geofences:
                inside |= gf.contains(lat, lng)
            if not inside:
                if config['QUIET'] is False:
                    log.info("{} ignored: located outside geofences.".format(name))
                return
        else:
            log.debug("Pokemon inside geofences was not checked because no geofences were set.")

        time_str = get_time_as_str(pkmn['disappear_time'], self.__timezone)
        pkmn.update({
            'pkmn': name,
            "dist": get_dist_as_str(dist) if dist != 'unkn' else 'unkn',
            'move1': move1,
            'move2': move2,
            'time_left': time_str[0],
            '12h_time': time_str[1],
            '24h_time': time_str[2],
            'dir': get_cardinal_dir([lat, lng], self.__latlng),
        })
        # Optional Stuff
        self.optional_arguments(pkmn)
        if config['QUIET'] is False:
            log.info("{} notification has been triggered!".format(name))

        threads = []
        # Spawn notifications in threads so they can work in background
        for alarm in self.__alarms:
            threads.append(gevent.spawn(alarm.pokemon_alert, pkmn))
            gevent.sleep(0)  # explict context yield

        for thread in threads:
            thread.join()

    def handle_pokestop(self, stop):
        # Quick check for enabled
        if self.__pokestop_filter['enabled'] is False:
            log.debug("Pokestop ignored: notifications are disabled.")
            return

        id_ = stop['id']

        # Check for previously processed (and make sure previous lure hasn't expired)
        if id_ in self.__pokestop_hist and self.__pokestop_hist[id_] >= datetime.utcnow():
            if config['QUIET'] is False:
                log.debug("Pokestop ({}) ignored: because it was previously notified.".format(id_))
            return

        self.__pokestop_hist[id_] = expire_time = stop['expire_time']

        # Check the time remaining
        seconds_left = (expire_time - datetime.utcnow()).total_seconds()
        if seconds_left < self.__time_limit:
            if config['QUIET'] is False:
                log.info("Pokestop ({}) ignored: only {} seconds remaining.".format(id_, seconds_left))
            return

        filt = self.__pokestop_filter

        # Check the distance from the set location
        lat, lng = stop['lat'], stop['lng']
        dist = get_earth_dist([lat, lng], self.__latlng)
        if dist != 'unkn':
            if dist < filt['min_dist'] or filt['max_dist'] < dist:
                if config['QUIET'] is False:
                    log.info("Pokestop ({}) ignored: distance was not in range {:.2f} to {:.2f}.".format(
                        id_, filt['min_dist'], filt['max_dist']))
                return
        else:
            log.debug("Pokestop distance was not checked because no location was set.")

        # Check if in geofences
        if len(self.__geofences) > 0:
            inside = False
            for gf in self.__geofences:
                inside |= gf.contains(lat, lng)
            if not inside:
                if config['QUIET'] is False:
                    log.info("Pokestop ignored: located outside geofences.")
                return
        else:
            log.debug("Pokestop inside geofences was not checked because no geofences were set.")

        time_str = get_time_as_str(expire_time, self.__timezone)
        stop.update({
            "dist": get_dist_as_str(dist) if dist != 'unkn' else 'unkn',
            'time_left': time_str[0],
            '12h_time': time_str[1],
            '24h_time': time_str[2],
            'dir': get_cardinal_dir([lat, lng], self.__latlng),
        })

        # Optional Stuff
        self.optional_arguments(stop)
        if config['QUIET'] is False:
            log.info("Pokestop ({}) notification has been triggered!".format(id_))

        threads = []
        # Spawn notifications in threads so they can work in background
        for alarm in self.__alarms:
            threads.append(gevent.spawn(alarm.pokestop_alert, stop))
            gevent.sleep(0)  # explict context yield

        for thread in threads:
            thread.join()

    def handle_gym(self, gym):
        # Quick check for enabled
        if self.__gym_filter['enabled'] is False:
            log.debug("Gym ignored: notifications are disabled.")
            return
        log.debug("Gyms set to {}.".format(self.__gym_filter['enabled']))

        id_ = gym['id']
        team_id = gym['team_id']
        old_team = self.__gym_hist.get(id_)

        # Ignore gyms when there is no change
        if (old_team == team_id):
            log.debug("Gym update ignored: team didn't change")
            return

        # Ignore changes to neutral
        if self.__gym_filter['ignore_neutral'] and team_id == 0:
            log.debug("Gym update ignored: changed to neutral")
            return

        self.__gym_hist[id_] = team_id

        # Ignore first time updates
        if old_team is None:
            log.debug("Gym update ignored: first time seeing gym")
            return

        if old_team not in self.__gym_filter and team_id not in self.__gym_filter:
            if config['QUIET'] is False:
                log.info("Gym update ignored: neither team is enabled")
            return

        lat, lng = gym['lat'], gym['lng']
        dist = get_earth_dist([lat, lng], self.__latlng)
        if dist != 'unkn':
            old_range, new_range = False, False
            old_f = self.__gym_filter.get(old_team)
            if old_f is not None:
                old_range = old_f['min_dist'] <= dist <= old_f['max_dist']
            new_f = self.__gym_filter.get(team_id)
            if new_f is not None:
                new_range = old_f['min_dist'] <= dist <= old_f['max_dist']
            if not old_range and not new_range:
                if config['QUIET'] is False:
                    log.info("Gym update ignored: both teams outside range")
        else:
            log.debug("Gym distance was not checked because no location was set.")

        # Check if in geofences
        if len(self.__geofences) > 0:
            inside = False
            for gf in self.__geofences:
                inside |= gf.contains(lat, lng)
            if inside is False:
                if config['QUIET'] is False:
                    log.info("Gym update ignored: located outside geofences.")
                return
        else:
            log.debug("Gym inside geofences was not checked because no geofences were set.")

        # Optional Stuff
        self.optional_arguments(gym)
        if config['QUIET'] is False:
            log.info("Gym ({}) notification has been triggered!".format(id_))

        gym.update({
            "dist": get_dist_as_str(dist) if dist != 'unkn' else 'unkn',
            'new_team': self.__team_name[team_id],
            'old_team': self.__team_name[old_team],
            'dir': get_cardinal_dir([lat, lng], self.__latlng),
        })

        threads = []
        # Spawn notifications in threads so they can work in background
        for alarm in self.__alarms:
            threads.append(gevent.spawn(alarm.gym_alert, gym))
            gevent.sleep(0)  # explict context yield

        for thread in threads:
            thread.join()

    # Retrieve optional requirements
    def optional_arguments(self, info):
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

    ##################################################  INITIALIZATION  ################################################

    def create_filters(self, file_path):
        # Load the filters file in
        with open(file_path, 'r') as f:
            filters = json.loads(f.read())

        # Set the Pokemon filter
        self.set_pokemon(filters.get('pokemon', {}))

        # Set the Pokestop filter
        self.set_pokestops(filters.get('pokestops', {}))

        # Set up Gym filter
        self.set_gyms(filters.get('gyms', {}))

    # Update the pokemon according to settings
    def set_pokemon(self, settings):
        # Start a new dict to track filters
        pokemon = {'enabled': settings.pop('enabled', False)}
        min_dist = float(settings.pop('min_dist', None) or 0)
        max_dist = float(settings.pop('max_dist', None) or 'inf')
        min_iv = float(settings.pop('min_iv', None) or 0)
        max_iv = float(settings.pop('max_iv', None) or 100)
        if pokemon['enabled']:
            log.info("Pokemon defaults: distance {:.2f} to {:.2f} / IV's {:.2f} to {:.2f}".format(
                min_dist, max_dist, min_iv, max_iv))
        for name in settings:
            pkmn_id = get_pkmn_id(name)
            if pkmn_id is None:
                log.error("Unable to find pokemon named {}...".format(name))
                continue
            if parse_boolean(settings[name]) is False:  # If set to false, set it as false
                log.debug("{} name set to 'false'. Skipping... ".format(name))
                continue
            else:
                try:
                    info = settings[name]
                    if parse_boolean(info):  # Allow all defaults
                        info = {}
                    pokemon[pkmn_id] = {
                        "min_dist": float(info.get('min_dist', None) or min_dist),
                        "max_dist": float(info.get('max_dist', None) or max_dist),
                        "min_iv": float(info.get('min_iv', None) or min_iv),
                        "max_iv": float(info.get('max_iv', None) or max_iv),
                        "move_1": info.get("move_1", None),
                        "move_2": info.get("move_2", None),
                        "move_set": info.get("move_set", None)
                    }
                    log.debug("#{} was set to the following: \n{}".format(
                        pkmn_id, json.dumps(pokemon[pkmn_id], sort_keys=True, indent=4)))
                except Exception as e:
                    log.error("Trying to set pokemon {} gave error: \n {}".format(pkmn_id, e))
                    log.debug("Stack trace: \n {}".format(traceback.format_exc()))
        self.__pokemon_filter = pokemon

    def set_pokestops(self, settings):
        pokestops = {
            "enabled": bool(parse_boolean(settings.pop('enabled', False))),
            "min_dist": float(settings.get('min_dist', None) or 0),
            "max_dist": float(settings.get('max_dist', None) or 'inf')
        }
        if pokestops['enabled']:
            log.info("Pokestop distance: {} to {}".format(pokestops['min_dist'], pokestops['max_dist']))
        self.__pokestop_filter = pokestops

    def set_gyms(self, settings):
        gyms = {
            "enabled": bool(parse_boolean(settings.pop('enabled', None)) or False),
            "ignore_neutral": bool(parse_boolean(settings.pop('ignore_neutral', None)) or False),
            "min_dist": float(settings.pop('min_dist', None) or 0),
            "max_dist": float(settings.pop('max_dist', None) or 'inf')
        }
        log.info("Gym distance: {:.2f} to {:.2f}. Ignoring Neutral set to {}".format(
            gyms['min_dist'], gyms['max_dist'], gyms['ignore_neutral']))

        for name in settings:
            team_id = get_team_id(name)
            if team_id is None:
                log.error("Unable to find team named {}...".format(name))
                continue
            if parse_boolean(settings[name]) is False:  # If set to false, skip altogether.
                log.debug("{} name set to 'false'. Skipping...".format(name))
                continue
            else:
                try:
                    info = settings[name]
                    if parse_boolean(info):  # Allow all defaults
                        info = {}
                    gyms[team_id] = {
                        "min_dist": float(info.get('min_dist', None) or gyms['min_dist']),
                        "max_dist": float(info.get('max_dist', None) or gyms['max_dist']),
                    }
                    log.debug("Team #{} was set to the following: {}".format(
                        team_id, json.dumps(gyms[team_id], sort_keys=True, indent=4)))
                except Exception as e:
                    log.error("Trying to set gym {} gave error: \n {}".format(team_id, e))
                    log.debug("Stack trace: \n {}".format(traceback.format_exc()))

        self.__gym_filter = gyms

    def create_geofences(self, file_path):
        geofences = {}
        with open(file_path, 'r') as file_:
            for line in file_:
                name = re.match("\[([^]]+)\]", line)
                if name:
                    cur = name.group(1)
                    geofences[cur] = []
                else:
                    geofences[cur].append([float(x) for x in line.split(",")])
        for name, points in geofences.iteritems():
            self.__geofences.append(Geofence(name, points))
            log.info("Geofence {} added.".format(name))
            log.debug("Geofence has the following points: \n {}".format(points))

    def update_locales(self):
        locale_path = os.path.join(get_path('locales'), '{}'.format(self.__locale))
        # Update pokemon names
        with open(os.path.join(locale_path, 'pokemon.json'), 'r') as f:
            names = json.loads(f.read())
            for pkmn_id, value in names.iteritems():
                self.__pokemon_name[int(pkmn_id)] = value
        # Update move names
        with open(os.path.join(locale_path, 'moves.json'), 'r') as f:
            moves = json.loads(f.read())
            for move_id, value in moves.iteritems():
                self.__move_name[int(move_id)] = value
        # Update team names
        with open(os.path.join(locale_path, 'teams.json'), 'r') as f:
            teams = json.loads(f.read())
            for team_id, value in teams.iteritems():
                self.__team_name[int(team_id)] = value

    ####################################################################################################################

    ##################################################  ALARM CREATION #################################################

    def create_alarms(self, file_path):
        with open(file_path, 'r') as f:
            alarm_settings = json.load(f)
        for alarm in alarm_settings:
            if parse_boolean(alarm['active']) is True:
                if alarm['type'] == 'boxcar':
                    from Boxcar import BoxcarAlarm
                    self.__alarms.append(BoxcarAlarm(alarm))
                elif alarm['type'] == 'discord':
                    from Discord import DiscordAlarm
                    self.__alarms.append(DiscordAlarm(alarm))
                elif alarm['type'] == 'facebook_page':
                    from FacebookPage import FacebookPageAlarm
                    self.__alarms.append(FacebookPageAlarm(alarm))
                elif alarm['type'] == 'pushbullet':
                    from Pushbullet import PushbulletAlarm
                    self.__alarms.append(PushbulletAlarm(alarm))
                elif alarm['type'] == 'pushover':
                    from Pushover import PushoverAlarm
                    self.__alarms.append(PushoverAlarm(alarm))
                elif alarm['type'] == 'slack':
                    from Slack import SlackAlarm
                    self.__alarms.append(SlackAlarm(alarm))
                elif alarm['type'] == 'telegram':
                    from Telegram import TelegramAlarm
                    self.__alarms.append(TelegramAlarm(alarm))
                elif alarm['type'] == 'twilio':
                    from Twilio import TwilioAlarm
                    self.__alarms.append(TwilioAlarm(alarm))
                elif alarm['type'] == 'twitter':
                    from Twitter import TwitterAlarm
                    self.__alarms.append(TwitterAlarm(alarm))
                else:
                    log.info("Alarm type not found: " + alarm['type'])
                self.set_optional_args(str(alarm))
            else:
                log.info("Alarm not activated: " + alarm['type'] + " because value not set to \"True\"")

    # Returns true if string contains an argument that requires
    def set_optional_args(self, line):
        # Reverse Location
        args = {'address', 'postal', 'neighborhood', 'sublocality', 'city', 'county', 'state', 'country'}
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

    ############################################## REQUIRES GOOGLE API KEY #############################################

    # Returns the LAT,LNG of a location given by either a name or coordinates
    def get_lat_lng_by_name(self, location_name):
        prog = re.compile("^(-?\d+\.\d+)[,\s]\s*(-?\d+\.\d+?)$")
        res = prog.match(location_name)
        latitude, longitude = None, None
        if res:
            latitude, longitude = float(res.group(1)), float(res.group(2))
        elif location_name:
            if self.__gmaps_client is None:  # Check if key was provided
                log.error("No Google Maps API key provided - unable to find location by name.")
                return []
            result = self.__gmaps_client.geocode(location_name)
            loc = result[0]['geometry']['location']  # Get the first (most likely) result
            latitude, longitude = loc.get("lat"), loc.get("lng")
        log.info("Location found: {:f}{:f}".format(latitude, longitude))
        return [latitude, longitude]

    # Returns the name of the location based on lat and lng
    def reverse_location(self, lat, lng):
        if self.__gmaps_client is None:  # Check if key was provided
            log.error("No Google Maps API key provided - unable to reverse geocode.")
            return {}
        details = {}
        try:
            result = self.__gmaps_client.reverse_geocode((lat, lng))[0]
            loc = {}
            for item in result['address_components']:
                for category in item['types']:
                    loc[category] = item['short_name']
            details = {
                'street_num': loc.get('street_number', 'unkn'),
                'street': loc.get('route', 'unkn'),
                'address': "{} {}".format(loc.get('street_number'), loc.get('route')),
                'postal': loc.get('postal_code', 'unkn'),
                'neighborhood': loc.get('neighborhood'),
                'sublocality': loc.get('sublocality'),
                'city': loc.get('locality', loc.get('postal_town')),  # try postal town if no city
                'county': loc.get('administrative_area_level_2'),
                'state': loc.get('administrative_area_level_1'),
                'country': loc.get('country')
            }
        except Exception as e:
            log.error("Encountered error while getting reverse location data ({}: {})".format(type(e).__name__, e))
            log.debug("Stack trace: \n {}".format(traceback.format_exc()))
        return details

    # Returns a set with walking dist and walking duration via Google Distance Matrix API
    def get_walking_data(self, lat, lng):
        if self.__latlng is None:
            log.error("No location has been set. Unable to get walking data.")
            return {}
        origin = "{},{}".format(self.__latlng[0], self.__latlng[1])
        dest = "{},{}".format(lat, lng)
        data = {'walk_dist': "!error!", 'walk_time': "!error!"}
        try:
            result = self.__gmaps_client.distance_matrix(origin, dest, mode='walking', units=config['UNITS'])
            result = result.get('rows')[0].get('elements')[0]
            data = {
                'walk_dist': result.get('distance').get('text').encode('utf-8'),
                'walk_time': result.get('duration').get('text').encode('utf-8'),
            }
        except Exception as e:
            log.error("Encountered error while getting walking data ({}: {})".format(type(e).__name__, e))
            log.debug("Stack trace: \n {}".format(traceback.format_exc()))
        return data

    # Returns a set with biking dist and biking duration via Google Distance Matrix API
    def get_biking_data(self, lat, lng):
        if self.__latlng is None:
            log.error("No location has been set. Unable to get biking data.")
            return {}
        origin = "{},{}".format(self.__latlng[0], self.__latlng[1])
        dest = "{},{}".format(lat, lng)
        data = {'bike_dist': "!error!", 'bike_time': "!error!"}
        try:
            result = self.__gmaps_client.distance_matrix(origin, dest, mode='bicycling', units=config['UNITS'])
            result = result.get('rows')[0].get('elements')[0]
            data = {
                'bike_dist': result.get('distance').get('text').encode('utf-8'),
                'bike_time': result.get('duration').get('text').encode('utf-8'),
            }
        except Exception as e:
            log.error("Encountered error while getting biking data ({}: {})".format(type(e).__name__, e))
            log.debug("Stack trace: \n {}".format(traceback.format_exc()))
        return data

    # Returns a set with driving dist and biking duration via Google Distance Matrix API
    def get_driving_data(self, lat, lng):
        if self.__latlng is None:
            log.error("No location has been set. Unable to get biking data.")
            return {}
        origin = "{},{}".format(self.__latlng[0], self.__latlng[1])
        dest = "{},{}".format(lat, lng)
        data = {'drive_dist': "!error!", 'drive_time': "!error!"}
        try:
            result = self.__gmaps_client.distance_matrix(origin, dest, mode='driving', units=config['UNITS'])
            result = result.get('rows')[0].get('elements')[0]
            data = {
                'drive_dist': result.get('distance').get('text').encode('utf-8'),
                'drive_time': result.get('duration').get('text').encode('utf-8'),
            }
        except Exception as e:
            log.error("Encountered error while getting driving data ({}: {})".format(type(e).__name__, e))
            log.debug("Stack trace: \n {}".format(traceback.format_exc()))
        return data

    ####################################################################################################################

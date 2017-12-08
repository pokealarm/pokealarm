# Standard Library Imports
import logging
from datetime import datetime

# 3rd Party Imports
from twitter import Twitter, OAuth

# Local Imports
from PokeAlarm.Alarms import Alarm
from PokeAlarm.Utils import parse_boolean, get_time_as_str, \
    require_and_remove_key, reject_leftover_parameters

log = logging.getLogger('Twitter')
try_sending = Alarm.try_sending
replace = Alarm.replace


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ATTENTION! !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#             ONLY EDIT THIS FILE IF YOU KNOW WHAT YOU ARE DOING!
# You DO NOT NEED to edit this file to customize messages! Please ONLY EDIT the
#     the 'alarms.json'. Failing to do so can cause other feature to break!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ATTENTION! !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


class TwitterAlarm(Alarm):

    _defaults = {
        'pokemon': {
            'status': "A wild <pkmn> has appeared!"
                      + " Available until <24h_time> (<time_left>). <gmaps>"
        },
        'pokestop': {
            'status': "Someone has placed a lure on a Pokestop! "
                      + "Lure will expire at <24h_time> (<time_left>). <gmaps>"
        },
        'gym': {
            'status': "A Team <old_team> gym has fallen! "
                      + "It is now controlled by <new_team>. <gmaps>"
        },
        'egg': {
            'status': "lvl <raid_level> raid! Hatches at <begin_24h_time>"
                      + "(<begin_time_left>). <gmaps>"
        },
        'raid': {
            'status': "Raid on <pkmn>! Available until <24h_time>"
                      + " (<time_left>). <gmaps>"
        }
    }

    # Gather settings and create alarm
    def __init__(self, settings):
        # Required Parameters
        self.__token = require_and_remove_key(
            'access_token', settings, "'Twitter' type alarms.")
        self.__token_key = require_and_remove_key(
            'access_secret', settings, "'Twitter' type alarms.")
        self.__con_secret = require_and_remove_key(
            'consumer_key', settings, "'Twitter' type alarms.")
        self.__con_secret_key = require_and_remove_key(
            'consumer_secret', settings, "'Twitter' type alarms.")
        self.__client = None

        # Optional Alarm Parameters
        self.__startup_message = parse_boolean(
            settings.pop('startup_message', "True"))

        # Optional Alert Parameters
        self.__pokemon = self.create_alert_settings(
            settings.pop('pokemon', {}), self._defaults['pokemon'])
        self.__pokestop = self.create_alert_settings(
            settings.pop('pokestop', {}), self._defaults['pokestop'])
        self.__gym = self.create_alert_settings(
            settings.pop('gym', {}), self._defaults['gym'])
        self.__egg = self.create_alert_settings(
            settings.pop('egg', {}), self._defaults['egg'])
        self.__raid = self.create_alert_settings(
            settings.pop('raid', {}), self._defaults['raid'])

        # Warn user about leftover parameters
        reject_leftover_parameters(settings, "'Alarm level in Twitter alarm.")

        log.info("Twitter Alarm has been created!")

    # Establish connection with Twitter
    def connect(self):
        self.__client = Twitter(
            auth=OAuth(self.__token, self.__token_key, self.__con_secret,
                       self.__con_secret_key))

    # Send a start up tweet
    def startup_message(self):
        if self.__startup_message:
            timestamps = get_time_as_str(datetime.utcnow())
            args = {
                "status": "{}- PokeAlarm activated!" .format(timestamps[2])
            }
            try_sending(log, self.connect, "Twitter", self.send_tweet, args)
            log.info("Startup tweet sent!")

    # Set the appropriate settings for each alert
    def create_alert_settings(self, settings, default):
        alert = {
            'status': settings.pop('status', default['status'])
        }
        reject_leftover_parameters(settings, "'Alert level in Twitter alarm.")
        return alert

    def send_alert(self, alert, info):
            limit = 140
            status = alert['status']
            if status.endswith("<gmaps>"):
                limit = 117  # Save 23 characters for the google maps
                status = status[:-7]  # Truncate gmaps
            status = replace(status[:limit], info)  # Truncate status
            if limit == 117:
                status += info['gmaps']  # Add in gmaps link
            args = {"status": status}
            try_sending(log, self.connect, "Twitter", self.send_tweet, args)

    # Trigger an alert based on Pokemon info
    def pokemon_alert(self, pokemon_info):
        self.send_alert(self.__pokemon, pokemon_info)

    # Trigger an alert based on Pokestop info
    def pokestop_alert(self, pokestop_info):
        self.send_alert(self.__pokestop, pokestop_info)

    # Trigger an alert based on Gym info
    def gym_alert(self, gym_info):
        self.send_alert(self.__gym, gym_info)

    # Trigger an alert when a raid egg has spawned (UPCOMING raid event)
    def raid_egg_alert(self, raid_info):
        self.send_alert(self.__egg, raid_info)

    # Trigger an alert based on Gym info
    def raid_alert(self, raid_info):
        self.send_alert(self.__raid, raid_info)

    # Send out a tweet with the given status
    def send_tweet(self, status):
        self.__client.statuses.update(status=status)

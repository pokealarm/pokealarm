# Standard Library Imports
from datetime import datetime
import logging
# 3rd Party Imports
from twitter import Twitter, OAuth
# Local Imports
from ..Alarm import Alarm
from ..Utils import parse_boolean, get_time_as_str, require_and_remove_key, reject_leftover_parameters

log = logging.getLogger('Twitter')
try_sending = Alarm.try_sending
replace = Alarm.replace


#####################################################  ATTENTION!  #####################################################
# You DO NOT NEED to edit this file to customize messages for services! Please see the Wiki on the correct way to
# customize services In fact, doing so will likely NOT work correctly with many features included in PokeAlarm.
#                               PLEASE ONLY EDIT IF YOU KNOW WHAT YOU ARE DOING!
#####################################################  ATTENTION!  #####################################################


class TwitterAlarm(Alarm):

    _defaults = {
        'pokemon': {
            'status': "A wild <pkmn> has appeared! Available until <24h_time> (<time_left>). <gmaps>",
        },
        'pokestop': {
            'status': "Someone has placed a lure on a Pokestop! Lure will expire at <24h_time> (<time_left>).  <gmaps>",
        },
        'gym': {
            'status': "A Team <old_team> gym has fallen! It is now controlled by <new_team>. <gmaps>"
        }
    }

    # Gather settings and create alarm
    def __init__(self, settings):
        # Required Parameters
        self.__token = require_and_remove_key('access_token', settings, "'Twitter' type alarms.")
        self.__token_key = require_and_remove_key('access_secret', settings, "'Twitter' type alarms.")
        self.__con_secret = require_and_remove_key('consumer_key', settings, "'Twitter' type alarms.")
        self.__con_secret_key = require_and_remove_key('consumer_secret', settings, "'Twitter' type alarms.")

        # Optional Alarm Parameters
        self.__startup_message = parse_boolean(settings.pop('startup_message', "True"))

        # Optional Alert Parameters
        self.__pokemon = self.create_alert_settings(settings.pop('pokemon', {}), self._defaults['pokemon'])
        self.__pokestop = self.create_alert_settings(settings.pop('pokestop', {}), self._defaults['pokestop'])
        self.__gym = self.create_alert_settings(settings.pop('gyms', {}), self._defaults['gym'])

        # Connect and send startup messages
        self.__client = None

        reject_leftover_parameters(settings, "'Alarm level in Twitter alarm.")

        log.info("TWitter Alarm has been created!")

    # Establish connection with Twitter
    def connect(self):
        self.__client = Twitter(
            auth=OAuth(self.__token, self.__token_key, self.__con_secret, self.__con_secret_key))

    # Send a start up tweet
    def startup_message(self):
        if self.__startup_message:
            timestamps = get_time_as_str(datetime.utcnow())
            args = {"status": "{}- PokeAlarm activated!" .format(timestamps[2])}
            try_sending(log, self.connect, "Twitter", self.send_tweet, args)
            log.info("Start up tweet sent!")

    # Set the appropriate settings for each alert
    def create_alert_settings(self, settings, default):
        alert = {
            'status': settings.get('status', default['status'])
        }
        return alert

    def send_alert(self, alert, info):
            args = {"status": replace(alert['status'], info)}
            try_sending(log, self.connect, "Twitter", self.__client.statuses.update, args)

    # Trigger an alert based on Pokemon info
    def pokemon_alert(self, pokemon_info):
        self.send_alert(self.__pokemon, pokemon_info)

    # Trigger an alert based on Pokestop info
    def pokestop_alert(self, pokestop_info):
        self.send_alert(self.__pokestop, pokestop_info)

    # Trigger an alert based on Gym info
    def gym_alert(self, gym_info):
        self.send_alert(self.__gym, gym_info)

    # Send out a tweet with the given status
    def send_tweet(self, status):
        self.__client.statuses.update(status=status)

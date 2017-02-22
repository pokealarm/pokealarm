# Standard Library Imports
from datetime import datetime
import logging
# 3rd Party Imports
from twitter import Twitter, OAuth
# Local Imports
from ..Alarm import Alarm
from ..Utils import parse_boolean, get_time_as_str

MAX_TWEET_LEN = 140

log = logging.getLogger(__name__)
try_sending = Alarm.try_sending
replace = Alarm.replace


#####################################################  ATTENTION!  #####################################################
# You DO NOT NEED to edit this file to customize messages for services! Please see the Wiki on the correct way to
# customize services In fact, doing so will likely NOT work correctly with many features included in PokeAlarm.
#                               PLEASE ONLY EDIT IF YOU KNOW WHAT YOU ARE DOING!
#####################################################  ATTENTION!  #####################################################


class  TwitterAlarm(Alarm):

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
        # Service Info
        self.__token = settings['access_token']
        self.__token_key = settings['access_secret']
        self.__con_secret = settings['consumer_key']
        self.__con_secret_key = settings['consumer_secret']
        self.__startup_message = settings.get('startup_message', "True")
        self.__startup_list = settings.get('startup_list', "True")

        # Set Alerts
        self.__pokemon = self.set_alert(settings.get('pokemon', {}), self._defaults['pokemon'])
        self.__pokestop = self.set_alert(settings.get('pokestop', {}), self._defaults['pokestop'])
        self.__gym = self.set_alert(settings.get('gyms', {}), self._defaults['gym'])

        # Connect and send startup messages
        self.__client = None
        self.connect()
        timestamps = get_time_as_str(datetime.utcnow())
        if parse_boolean(self.__startup_message):
            self.__client.statuses.update(status="%s - PokeAlarm has intialized!" % timestamps[2])
        log.info("Twitter Alarm intialized.")

    # Establish connection with Twitter
    def connect(self):
        self.__client = Twitter(
            auth=OAuth(self.__token, self.__token_key, self.__con_secret, self.__con_secret_key))

    # Set the appropriate settings for each alert
    def set_alert(self, settings, default):
        alert = {
            'status': settings.get('status', default['status'])
        }
        return alert

    # Post Pokemon Status
    def send_alert(self, alert, info):
        args = {"status": replace(alert['status'], info)[:MAX_TWEET_LEN]}
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

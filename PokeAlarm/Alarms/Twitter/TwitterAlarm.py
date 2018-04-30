# Standard Library Imports
import re
from datetime import datetime

# 3rd Party Imports
from twitter import Twitter, OAuth

# Local Imports
from PokeAlarm.Alarms import Alarm
from PokeAlarm.Utils import parse_boolean, get_time_as_str, \
    require_and_remove_key, reject_leftover_parameters

try_sending = Alarm.try_sending
replace = Alarm.replace
url_regex = re.compile(
    "(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]"
    "@!\$&'\(\)\*\+,;=.]+", re.I)


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ATTENTION! !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#             ONLY EDIT THIS FILE IF YOU KNOW WHAT YOU ARE DOING!
# You DO NOT NEED to edit this file to customize messages! Please ONLY EDIT the
#     the 'alarms.json'. Failing to do so can cause other feature to break!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ATTENTION! !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


class TwitterAlarm(Alarm):

    _defaults = {
        'monsters': {
            'status': "A wild <mon_name> has appeared! "
                      "Available until <24h_time> (<time_left>). <gmaps>"
        },
        'stops': {
            'status': "Someone has placed a lure on a Pokestop! "
                      "Lure will expire at <24h_time> (<time_left>). <gmaps>"
        },
        'gyms': {
            'status': "A Team <old_team> gym has fallen! "
                      "It is now controlled by <new_team>. <gmaps>"
        },
        'eggs': {
            'status': "Level <egg_lvl> raid incoming! Hatches at "
                      "<24h_hatch_time> (<hatch_time_left>). <gmaps>"
        },
        'raids': {
            'status': "Raid <raid_lvl> against <mon_name>! Available until "
                      "<24h_raid_end> (<raid_time_left>). <gmaps>"
        },
        'weather': {
            'status': "The weather around <lat>,<lng> has changed"
                      " to <weather>!"
        }
    }

    # Gather settings and create alarm
    def __init__(self, mgr, settings):
        self._log = mgr.get_child_logger("alarms")

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
            settings.pop('monsters', {}), self._defaults['monsters'])
        self.__pokestop = self.create_alert_settings(
            settings.pop('stops', {}), self._defaults['stops'])
        self.__gym = self.create_alert_settings(
            settings.pop('gyms', {}), self._defaults['gyms'])
        self.__egg = self.create_alert_settings(
            settings.pop('eggs', {}), self._defaults['eggs'])
        self.__raid = self.create_alert_settings(
            settings.pop('raids', {}), self._defaults['raids'])
        self.__weather = self.create_alert_settings(
            settings.pop('weather', {}), self._defaults['weather'])

        # Warn user about leftover parameters
        reject_leftover_parameters(settings, "'Alarm level in Twitter alarm.")

        self._log.info("Twitter Alarm has been created!")

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
            try_sending(
                self._log, self.connect, "Twitter", self.send_tweet, args)

            self._log.info("Startup tweet sent!")

    # Set the appropriate settings for each alert
    def create_alert_settings(self, settings, default):
        alert = {
            'status': settings.pop('status', default['status'])
        }
        reject_leftover_parameters(settings, "'Alert level in Twitter alarm.")
        return alert

    # Shortens the tweet down, calculating for urls being shortened
    def shorten(self, message, limit=280, url_length=23):
        msg = ""
        for word in re.split(r'\s', message):
            word_len = len(word)
            if url_regex.match(word):  # If it's a url
                if limit <= url_length:  # if the whole thing doesn't fit
                    break  # Don't add the url
                word_len = url_length  # URL's have a fixed length
            elif word_len >= limit:  # If the word doesn't fit
                word_len = limit - 1
                word = word[:word_len]  # truncate it
            limit -= word_len + 1  # word + space
            msg += " " + word
        print msg
        return msg[1:]  # Strip the space

    def send_alert(self, alert, info):
        args = {
            "status": self.shorten(replace(alert['status'], info))
        }
        try_sending(self._log, self.connect, "Twitter", self.send_tweet, args)

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

    # Trigger an alert based on weather webhook
    def weather_alert(self, weather_info):
        self.send_alert(self.__weather, weather_info)

    # Send out a tweet with the given status
    def send_tweet(self, status):
        self.__client.statuses.update(status=status)

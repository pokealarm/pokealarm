# Standard Library Imports

# 3rd Party Imports
from twilio.rest import TwilioRestClient

# Local Imports
from PokeAlarm.Alarms import Alarm
from PokeAlarm.Utils import parse_boolean, require_and_remove_key, \
    reject_leftover_parameters

try_sending = Alarm.try_sending
replace = Alarm.replace


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ATTENTION! !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#             ONLY EDIT THIS FILE IF YOU KNOW WHAT YOU ARE DOING!
# You DO NOT NEED to edit this file to customize messages! Please ONLY EDIT the
#     the 'alarms.json'. Failing to do so can cause other feature to break!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ATTENTION! !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


class TwilioAlarm(Alarm):

    _defaults = {
        'monsters': {
            'message': "A wild <mon_name> has appeared! <gmaps> "
                       "Available until <24h_time> (<time_left>)."
        },
        'stops': {
            'message': "Someone has placed a lure on a Pokestop! <gmaps>"
                       "Lure will expire at <24h_time> (<time_left>)."
        },
        'gyms': {
            'message': "A Team <old_team> gym has fallen! <gmaps>"
                       "It is now controlled by <new_team>."
        },
        'eggs': {
            'message': "A level <egg_lvl> raid is incoming! <gmaps>"
                       "Egg hatches <24h_hatch_time> (<hatch_time_left>)."
        },
        'raids': {
            'message': "Level <raid_lvl> raid against <mon_name>! <gmaps>"
                       " Available until <24h_raid_end> (<raid_time_left>)."
        },
        'weather': {
            'message': "The weather around <lat>,<lng> has"
                       " changed to <weather>!"
        }
    }

    # Gather settings and create alarm
    def __init__(self, mgr, settings):
        self._log = mgr.get_child_logger("alarms")

        # Required Parameters
        self.__account_sid = require_and_remove_key(
            'account_sid', settings, "'Twilio' type alarms.")
        self.__auth_token = require_and_remove_key(
            'auth_token', settings, "'Twilio' type alarms.")
        self.__from_number = require_and_remove_key(
            'from_number', settings, "'Twilio' type alarms.")
        self.__to_number = require_and_remove_key(
            'to_number', settings, "'Twilio' type alarms.")
        self.__client = None

        # Optional Alarm Parameters
        self.__startup_message = parse_boolean(
            settings.pop('startup_message', "True"))

        # Optional Alert Parameters
        self.__pokemon = self.set_alert(
            settings.pop('monsters', {}), self._defaults['monsters'])
        self.__pokestop = self.set_alert(
            settings.pop('stops', {}), self._defaults['stops'])
        self.__gym = self.set_alert(
            settings.pop('gyms', {}), self._defaults['gyms'])
        self.__egg = self.set_alert(
            settings.pop('eggs', {}), self._defaults['eggs'])
        self.__raid = self.set_alert(
            settings.pop('raids', {}), self._defaults['raids'])
        self.__weather = self.set_alert(
            settings.pop('weather', {}), self._defaults['weather'])

        # Warn user about leftover parameters
        reject_leftover_parameters(settings, "'Alarm level in Twilio alarm.")

        self._log.info("Twilio Alarm has been created!")

    # (Re)establishes Twilio connection
    def connect(self):
        self.__client = TwilioRestClient(self.__account_sid, self.__auth_token)

    # Send a message letting the channel know that this alarm started
    def startup_message(self):
        if self.__startup_message:
            self.send_sms(
                to_num=self.__to_number,
                from_num=self.__from_number,
                body="PokeAlarm activated!"
            )
            self._log.info("Startup message sent!")

    # Set the appropriate settings for each alert
    def set_alert(self, settings, default):
        alert = {
            'to_number': settings.pop('to_number', self.__to_number),
            'from_number': settings.pop('from_number', self.__from_number),
            'message': settings.pop('message', default['message'])
        }
        reject_leftover_parameters(settings, "'Alert level in Twilio alarm.")
        return alert

    # Send Pokemon Info
    def send_alert(self, alert, info):
        self.send_sms(
            to_num=alert['to_number'],
            from_num=alert['from_number'],
            body=replace(alert['message'], info)
        )

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

    # Trigger an alert based on Raid info
    def raid_alert(self, raid_info):
        self.send_alert(self.__raid, raid_info)

    # Trigger an alert based on Weather info
    def weather_alert(self, weather_info):
        self.send_alert(self.__weather, weather_info)

    # Send a SMS message
    def send_sms(self, to_num, from_num, body):
        if not isinstance(to_num, list):
            to_num = [to_num]
        for num in to_num:
            args = {
                'to': num,
                'from_': from_num,
                'body': body
            }
            try_sending(
                self._log, self.connect, "Twilio",
                self.__client.messages.create, args)

# Standard Library Imports
import logging
# 3rd Party Imports
from twilio.rest import TwilioRestClient
# Local Imports
from ..Alarm import Alarm
from ..Utils import parse_boolean, require_and_remove_key, reject_leftover_parameters

log = logging.getLogger('Twilio')
try_sending = Alarm.try_sending
replace = Alarm.replace


#####################################################  ATTENTION!  #####################################################
# You DO NOT NEED to edit this file to customize messages for services! Please see the Wiki on the correct way to
# customize services In fact, doing so will likely NOT work correctly with many features included in PokeAlarm.
#                               PLEASE ONLY EDIT IF YOU KNOW WHAT YOU ARE DOING!
#####################################################  ATTENTION!  #####################################################


class TwilioAlarm(Alarm):

    _defaults = {
        'pokemon': {
            'message': "A wild <pkmn> has appeared! <gmaps> Available until <24h_time> (<time_left>)."
        },
        'pokestop': {
            'message': "Someone has placed a lure on a Pokestop! <gmaps> Lure will expire at <24h_time> (<time_left>)."
        },
        'gym': {
            'message': "A Team <old_team> gym has fallen! It is now controlled by <new_team>. <gmaps>"
        },
        'egg': {
            'message': "A level <raid_level> raid is incoming! <gmap> Egg hatches <begin_24h_time> (<begin_time_left>)."
        },
        'raid': {
           'message': "A raid on <pkmn> is available! <gmap> Available until <24h_time> (<time_left>)."
        }
    }

    # Gather settings and create alarm
    def __init__(self, settings):
        # Required Parameters
        self.__account_sid = require_and_remove_key('account_sid', settings, "'Twilio' type alarms.")
        self.__auth_token = require_and_remove_key('auth_token', settings, "'Twilio' type alarms.")
        self.__from_number = require_and_remove_key('from_number', settings, "'Twilio' type alarms.")
        self.__to_number = require_and_remove_key('to_number', settings, "'Twilio' type alarms.")
        self.__client = None

        # Optional Alarm Parameters
        self.__startup_message = parse_boolean(settings.pop('startup_message', "True"))

        # Optional Alert Parameters
        self.__pokemon = self.set_alert(settings.pop('pokemon', {}), self._defaults['pokemon'])
        self.__pokestop = self.set_alert(settings.pop('pokestop', {}), self._defaults['pokestop'])
        self.__gym = self.set_alert(settings.pop('gyms', {}), self._defaults['gym'])
        self.__egg = self.set_alert(settings.pop('egg', {}), self._defaults['egg'])
        self.__raid = self.set_alert(settings.pop('raid', {}), self._defaults['raid'])

        # Warn user about leftover parameters
        reject_leftover_parameters(settings, "'Alarm level in Twilio alarm.")

        log.info("Twilio Alarm has been created!")


    # (Re)establishes Telegram connection
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
            log.info("Startup message sent!")

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

    # Send a SMS message
    def send_sms(self, to_num, from_num, body):
        if not isinstance(to_num, list):
           to_num = [to_num]
        for num in to_num:
            args={
                'to': num,
                'from_': from_num,
                'body': body
            }
            try_sending(log, self.connect, "Twilio", self.__client.messages.create, args)

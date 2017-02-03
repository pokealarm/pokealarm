# Standard Library Imports
import logging
# 3rd Party Imports
from twilio.rest import TwilioRestClient
# Local Imports
from ..Alarm import Alarm
from ..Utils import parse_boolean

log = logging.getLogger(__name__)
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
            # 'from_number': Required
            # 'to_number': Required
            'message': "A wild <pkmn> has appeared! <gmaps> Available until <24h_time> (<time_left>).",
        },
        'pokestop': {
            # 'from_number': Required
            # 'to_number': Required
            'message': "Someone has placed a lure on a Pokestop! <gmaps> Lure will expire at <24h_time> (<time_left>).",
        },
        'gym': {
            # 'from_number': Required
            # 'to_number': Required
            'message': "A Team <old_team> gym has fallen! It is now controlled by <new_team>. <gmaps>",
        }
    }

    # Gather settings and create alarm
    def __init__(self, settings):
        # Service Info
        self.__account_sid = settings['account_sid']
        self.__auth_token = settings['auth_token']

        self.__from_number = settings.get('from_number')
        self.__to_number = settings.get('to_number')
        self.__startup_message = settings.get('startup_message', "True")
        self.__startup_list = settings.get('startup_message', "True")

        # Set Alerts
        self.__pokemon = self.set_alert(settings.get('pokemon', {}), self._defaults['pokemon'])
        self.__pokestop = self.set_alert(settings.get('pokestop', {}), self._defaults['pokestop'])
        self.__gym = self.set_alert(settings.get('gyms', {}), self._defaults['gym'])

        # Connect and send startup messages
        self.__client = None
        self.connect()
        if parse_boolean(self.__startup_message):
            self.send_sms(
                to_num=self.__pokemon['to_number'],
                from_num=self.__pokemon['from_number'],
                msg="PokeAlarm has been activated! We will text this number about pokemon.")
        log.info("Twilio Alarm intialized.")

    # (Re)establishes Telegram connection
    def connect(self):
        self.__client = TwilioRestClient(self.__account_sid, self.__auth_token)

    # Set the appropriate settings for each alert
    def set_alert(self, settings, default):
        alert = {
            'to_number': settings.get('to_number', self.__to_number),
            'from_number': settings.get('from_number', self.__from_number),
            'message': settings.get('message', default['message'])
        }

        return alert

    # Send Pokemon Info
    def send_alert(self, alert, info):
        args = {
            'to_num': alert['to_number'],
            'from_num': alert['from_number'],
            'msg': replace(alert['message'], info)
        }
        try_sending(log, self.connect, "Twilio", self.send_sms, args)

    # Trigger an alert based on Pokemon info
    def pokemon_alert(self, pokemon_info):
        self.send_alert(self.__pokemon, pokemon_info)

    # Trigger an alert based on Pokestop info
    def pokestop_alert(self, pokestop_info):
        self.send_alert(self.__pokestop, pokestop_info)

    # Trigger an alert based on Gym info
    def gym_alert(self, gym_info):
        self.send_alert(self.__gym, gym_info)

    # Send message through Twilio
    def send_sms(self, to_num, from_num, msg):
        message = self.__client.messages.create(body=msg, to=to_num, from_=from_num)

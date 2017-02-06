# Standard Library Imports
from datetime import datetime
import logging
# 3rd Party Imports
import facebook
# Local Imports
from ..Alarm import Alarm
from ..Utils import parse_boolean, get_time_as_str

log = logging.getLogger(__name__)
try_sending = Alarm.try_sending
replace = Alarm.replace


#####################################################  ATTENTION!  #####################################################
# You DO NOT NEED to edit this file to customize messages for services! Please see the Wiki on the correct way to
# customize services In fact, doing so will likely NOT work correctly with many features included in PokeAlarm.
#                               PLEASE ONLY EDIT IF YOU KNOW WHAT YOU ARE DOING!
#####################################################  ATTENTION!  #####################################################


class FacebookPageAlarm(Alarm):

    _defaults = {
        'pokemon': {
            'message': "A wild <pkmn> has appeared! Available until <24h_time> (<time_left>).",
            'link': "<gmaps>"
        },
        'pokestop': {
            'message': "Someone has placed a lure on a Pokestop! Lure will expire at <24h_time> (<time_left>).",
            'link': "<gmaps>"
        },
        'gym': {
            'message': "A Team <old_team> gym has fallen! It is now controlled by <new_team>.",
            'link': "<gmaps>"
        }
    }

    # Gather settings and create alarm
    def __init__(self, settings):
        # Service Info
        self.__page_access_token = settings['page_access_token']
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
            self.__client.put_wall_post(message="{} - PokeAlarm has intialized!".format(timestamps[2]))
        log.info("FacebookPage Alarm intialized.")

    # Establish connection with FacebookPage
    def connect(self):
        self.__client = facebook.GraphAPI(self.__page_access_token)

    # Set the appropriate settings for each alert
    def set_alert(self, settings, default):
        alert = {
            'message': settings.get('message', default['message']),
            'link': settings.get('link', default['link'])
        }
        return alert

    # Post Pokemon Message
    def send_alert(self, alert, info):
        args = {
            "message": replace(alert['message'], info),
            "attachment": {"link": replace(alert['link'], info)}
        }

        try_sending(log, self.connect, "FacebookPage", self.__client.put_wall_post, args)

    # Trigger an alert based on Pokemon info
    def pokemon_alert(self, pokemon_info):
        self.send_alert(self.__pokemon, pokemon_info)

    # Trigger an alert based on Pokestop info
    def pokestop_alert(self, pokestop_info):
        self.send_alert(self.__pokestop, pokestop_info)

    # Trigger an alert based on Gym info
    def gym_alert(self, gym_info):
        self.send_alert(self.__gym, gym_info)

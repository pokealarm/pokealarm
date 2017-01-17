# Standard Library Imports
import logging
# 3rd Party Imports
from pushbullet import PushBullet
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


class PushbulletAlarm(Alarm):

    _defaults = {
        'pokemon': {
            'title': "A wild <pkmn> has appeared!",
            'url': "<gmaps>",
            'body': "Available until <24h_time> (<time_left>)."
        },
        'pokestop': {
            'title': "Someone has placed a lure on a Pokestop!",
            'url': "<gmaps>",
            'body': "Lure will expire at <24h_time> (<time_left>)."
        },
        'gym': {
            'title': "A Team <old_team> gym has fallen!",
            'url': "<gmaps>",
            'body': "It is now controlled by <new_team>."
        }
    }

    # Gather settings and create alarm
    def __init__(self, settings):
        # Service Info
        self.__api_key = settings['api_key']
        self.__startup_message = settings.get('startup_message', "True")
        self.__startup_list = settings.get('startup_list', "True")

        # Set Alerts
        self.__pokemon = self.set_alert(settings.get('pokemon', {}), self._defaults['pokemon'])
        self.__pokestop = self.set_alert(settings.get('pokestop', {}), self._defaults['pokestop'])
        self.__gym = self.set_alert(settings.get('gyms', {}), self._defaults['gym'])

        # Connect and send startup messages
        self.__client = None
        self.connect()
        if parse_boolean(self.__startup_message):
            self.__pokemon['sender'].push_note("PokeAlarm activated!", "We will alert you about pokemon.")
        log.info("Pushbullet Alarm intialized.")

    # (Re)establishes Pushbullet connection
    def connect(self):
        self.__client = PushBullet(self.__api_key)
        self.__pokemon['sender'] = self.get_sender(self.__client, self.__pokemon['channel'])
        self.__pokestop['sender'] = self.get_sender(self.__client, self.__pokestop['channel'])
        self.__gym['sender'] = self.get_sender(self.__client, self.__gym['channel'])

    # Set the appropriate settings for each alert
    def set_alert(self, settings, default):
        alert = {
            'title': settings.get('title', default['title']),
            'url': settings.get('url', default['url']),
            'body': settings.get('body', default['body']),
            'channel': settings.get('channel')
        }
        return alert

    # Send Alert to Pushbullet
    def send_alert(self, alert, info):
        args = {
            'title': replace(alert['title'], info),
            'url': replace(alert['url'], info),
            'body': replace(alert['body'], info)
        }
        try_sending(log, self.connect, "PushBullet", alert['sender'].push_link, args)

    # Trigger an alert based on Pokemon info
    def pokemon_alert(self, pokemon_info):
        self.send_alert(self.__pokemon, pokemon_info)

    # Trigger an alert based on Pokestop info
    def pokestop_alert(self, pokestop_info):
        self.send_alert(self.__pokestop, pokestop_info)

    # Trigger an alert based on Gym info
    def gym_alert(self, gym_info):
        self.send_alert(self.__gym, gym_info)

    # Attempt to get the channel, otherwise default to all devices
    def get_sender(self, client, channel_tag):
        req_channel = next((channel for channel in client.channels
                            if channel.channel_tag == channel_tag), self.__client)
        if req_channel is self.__client and channel_tag is not None:
            log.error("Unable to find channel... Pushing to all devices instead...")
        else:
            log.info("Pushing to channel %s." % channel_tag)
        return req_channel

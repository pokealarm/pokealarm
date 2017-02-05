# Standard Library Imports
import logging
import re
# 3rd Party Imports
from slacker import Slacker
# Local Imports
from ..Alarm import Alarm
from ..Utils import parse_boolean, get_static_map_url

log = logging.getLogger('Slack')
try_sending = Alarm.try_sending
replace = Alarm.replace


#####################################################  ATTENTION!  #####################################################
# You DO NOT NEED to edit this file to customize messages for services! Please see the Wiki on the correct way to
# customize services In fact, doing so will likely NOT work correctly with many features included in PokeAlarm.
#                               PLEASE ONLY EDIT IF YOU KNOW WHAT YOU ARE DOING!
#####################################################  ATTENTION!  #####################################################


class SlackAlarm(Alarm):

    _defaults = {
        'pokemon': {
            # 'channel':"general",
            'username': "<pkmn>",
            'icon_url': "https://raw.githubusercontent.com/kvangent/PokeAlarm/master/icons/<pkmn_id>.png",
            'title': "A wild <pkmn> has appeared!",
            'url': "<gmaps>",
            'body': "Available until <24h_time> (<time_left>)."
        },
        'pokestop': {
            # 'channel':"general",
            'username': "Pokestop",
            'icon_url': "https://raw.githubusercontent.com/kvangent/PokeAlarm/master/icons/pokestop.png",
            'title': "Someone has placed a lure on a Pokestop!",
            'url': "<gmaps>",
            'body': "Lure will expire at <24h_time> (<time_left>)."
        },
        'gym': {
            # 'channel':"general",
            'username': "<new_team> Gym Alerts",
            'icon_url': "https://raw.githubusercontent.com/kvangent/PokeAlarm/master/icons/gym_<new_team>.png",
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
        self.__channel = settings.get('channel', "general")
        self.__map = settings.get('map', {})
        self.__startup_list = settings.get('startup_list', "True")

        # Set Alerts
        self.__pokemon = self.set_alert(settings.get('pokemon', {}), self._defaults['pokemon'])
        self.__pokestop = self.set_alert(settings.get('pokestop', {}), self._defaults['pokestop'])
        self.__gym = self.set_alert(settings.get('gym', {}), self._defaults['gym'])

        # Connect and send startup messages
        self.__client = None
        self.__channels = {}
        self.connect()
        if parse_boolean(self.__startup_message):
            self.__client.chat.post_message(
                channel=self.get_channel(self.__pokemon['channel']),
                username='PokeAlarm',
                text='PokeAlarm activated! We will alert this channel about pokemon.'
            )
        log.info("Slack Alarm intialized.")
        log.debug("Attempting to push to the following channels: Pokemon:{}, Pokestops:{}, Gyms:{}".format(
            self.__pokemon['channel'], self.__pokestop['channel'], self.__gym['channel']))

    # Establish connection with Slack
    def connect(self):
        self.__client = Slacker(self.__api_key)
        self.update_channels()

    # Set the appropriate settings for each alert
    def set_alert(self, settings, default):
        alert = {
            'channel': settings.get('channel', self.__channel),
            'username': settings.get('username', default['username']),
            'icon_url': settings.get('icon_url', default['icon_url']),
            'title': settings.get('title', default['title']),
            'url': settings.get('url', default['url']),
            'body': settings.get('body', default['body']),
            'map': get_static_map_url(settings.get('map', self.__map))
        }
        return alert

    # Send Alert to Slack
    def send_alert(self, alert, info):
        args = {
            'channel': self.get_channel(replace(alert['channel'], info)),
            'username': replace(alert['username'], info),
            'text': '<{}|{}> - {}'.format(replace(alert['url'], info), replace(alert['title'], info),
                                          replace(alert['body'], info)),
            'icon_url': replace(alert['icon_url'], info),
            'attachments': self.make_map(alert['map'], info['lat'], info['lng'])
        }

        try_sending(log, self.connect, "Slack", self.__client.chat.post_message, args)

    # Trigger an alert based on Pokemon info
    def pokemon_alert(self, pokemon_info):
        self.send_alert(self.__pokemon, pokemon_info)

    # Trigger an alert based on Pokestop info
    def pokestop_alert(self, pokestop_info):
        self.send_alert(self.__pokestop, pokestop_info)

    # Trigger an alert based on Pokestop info
    def gym_alert(self, gym_info):
        self.send_alert(self.__gym, gym_info)

    # Update channels list
    def update_channels(self):
        self.__channels = {}
        response = self.__client.channels.list(True).body
        for channel in response['channels']:
            self.__channels[channel['name']] = channel['id']
        response = self.__client.groups.list().body
        for channel in response['groups']:
            self.__channels[channel['name']] = channel['id']
        log.debug(self.__channels)

    # Checks for valid channel, otherwise defaults to general
    def get_channel(self, name):
        channel = SlackAlarm.channel_format(name)
        if channel not in self.__channels:
            if name == self.__channel:
                log.error("Default channel %s not found... Posting to general instead." % channel)
                return "#general"
            else:
                log.debug("No channel created named %s... Reverting to default." % channel)
                default = self.get_channel(self.__channel)
                return default
        return channel

    # Returns a string s that is in proper channel format
    @staticmethod
    def channel_format(name):
        if name[0] == '#':  # Remove # if added
            name = name[1:]
        name = name.replace(u"\u2642", "m").replace(u"\u2640", "f").lower()
        pattern = re.compile("[^_a-z0-9-]+")
        return pattern.sub("", name)

    # Build a query for a static map of the pokemon location
    @staticmethod
    def make_map( map_url, lat, lng):
        if map_url is None:  # If no map is set
            return None
        map = [{
            'fallback': 'Map_Preview',
            'image_url': replace(map_url, {'lat': lat, 'lng': lng})
        }]
        log.debug(map[0].get('image_url'))
        return map

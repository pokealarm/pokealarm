# Standard Library Imports
import logging
import re
# 3rd Party Imports
from slacker import Slacker
# Local Imports
from ..Alarm import Alarm
from ..Utils import parse_boolean, get_static_map_url, require_and_remove_key, reject_leftover_parameters

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
            'username': "<pkmn>",
            'icon_url': "https://raw.githubusercontent.com/RocketMap/PokeAlarm/master/icons/<pkmn_id>.png",
            'title': "A wild <pkmn> has appeared!",
            'url': "<gmaps>",
            'body': "Available until <24h_time> (<time_left>)."
        },
        'pokestop': {
            'username': "Pokestop",
            'icon_url': "https://raw.githubusercontent.com/RocketMap/PokeAlarm/master/icons/pokestop.png",
            'title': "Someone has placed a lure on a Pokestop!",
            'url': "<gmaps>",
            'body': "Lure will expire at <24h_time> (<time_left>)."
        },
        'gym': {
            'username': "<new_team> Gym Alerts",
            'icon_url': "https://raw.githubusercontent.com/RocketMap/PokeAlarm/master/icons/gym_<new_team_id>.png",
            'title': "A Team <old_team> gym has fallen!",
            'url': "<gmaps>",
            'body': "It is now controlled by <new_team>."
        },
        'egg': {
            'username': "Egg",
            'icon_url': "https://raw.githubusercontent.com/RocketMap/PokeAlarm/master/icons/egg_<raid_level>.png",
            'title': "A level <raid_level> raid is incoming!",
            'url': "<gmaps>",
            'body': "The egg will hatch <begin_24h_time> (<begin_time_left>)."
        },
        'raid': {
            'username': "<pkmn> Raid",
            'icon_url': "https://raw.githubusercontent.com/RocketMap/PokeAlarm/master/icons/<pkmn_id>.png",
            'title': "A Raid is available against <pkmn>!",
            'url': "<gmaps>",
            'body': "The raid is available until <24h_time> (<time_left>)."
        }
    }

    # Gather settings and create alarm
    def __init__(self, settings, static_map_key):
        # Required Parameters
        self.__api_key = require_and_remove_key('api_key', settings, "'Slack' type alarms.")
        self.__default_channel = self.channel_format(
            require_and_remove_key('channel', settings, "'Slack' type alarms."))
        self.__client = None
        self.__channels = {}

        # Optional Alarm Parameters
        self.__startup_message = parse_boolean(settings.pop('startup_message', "True"))
        self.__map = settings.pop('map', {})
        self.__static_map_key = static_map_key

        # Optional Alert Parameters
        self.__pokemon = self.create_alert_settings(settings.pop('pokemon', {}), self._defaults['pokemon'])
        self.__pokestop = self.create_alert_settings(settings.pop('pokestop', {}), self._defaults['pokestop'])
        self.__gym = self.create_alert_settings(settings.pop('gym', {}), self._defaults['gym'])
        self.__egg = self.create_alert_settings(settings.pop('egg', {}), self._defaults['egg'])
        self.__raid = self.create_alert_settings(settings.pop('raid', {}), self._defaults['raid'])

        # Warn user about leftover parameters
        reject_leftover_parameters(settings, "'Alarm level in Slack alarm.")

        log.info("Slack Alarm has been created!")

    # Establish connection with Slack
    def connect(self):
        self.__client = Slacker(self.__api_key)
        self.update_channels()

    # Send a message letting the channel know that this alarm started
    def startup_message(self):
        if self.__startup_message:
            self.send_message(self.__default_channel, username="PokeAlarm", text="PokeAlarm activated!")
            log.info("Startup message sent!")

    # Set the appropriate settings for each alert
    def create_alert_settings(self, settings, default):
        alert = {
            'channel': settings.pop('channel', self.__default_channel),
            'username': settings.pop('username', default['username']),
            'icon_url': settings.pop('icon_url', default['icon_url']),
            'title': settings.pop('title', default['title']),
            'url': settings.pop('url', default['url']),
            'body': settings.pop('body', default['body']),
            'map': get_static_map_url(settings.pop('map', self.__map), self.__static_map_key)
        }
        reject_leftover_parameters(settings, "'Alert level in Slack alarm.")
        return alert

    # Send Alert to Slack
    def send_alert(self, alert, info):
        attachments = [{
            'fallback': 'Map_Preview',
            'image_url': replace( alert['map'], {'lat': info['lat'], 'lng':info['lng']})
        }] if alert['map'] is not None else None
        self.send_message(
            channel=replace(alert['channel'], info),
            username=replace(alert['username'], info),
            text='<{}|{}> - {}'.format(replace(alert['url'], info), replace(alert['title'], info),
                                          replace(alert['body'], info)),
            icon_url=replace(alert['icon_url'], info),
            attachments=attachments
        )

    # Trigger an alert based on Pokemon info
    def pokemon_alert(self, pokemon_info):
        self.send_alert(self.__pokemon, pokemon_info)

    # Trigger an alert based on Pokestop info
    def pokestop_alert(self, pokestop_info):
        self.send_alert(self.__pokestop, pokestop_info)

    # Trigger an alert based on Pokestop info
    def gym_alert(self, gym_info):
        self.send_alert(self.__gym, gym_info)

    # Trigger an alert when a raid egg has spawned (UPCOMING raid event)
    def raid_egg_alert(self, raid_info):
        self.send_alert(self.__egg, raid_info)

    # Trigger an alert based on Gym info
    def raid_alert(self, raid_info):
        self.send_alert(self.__raid, raid_info)

    # Get a list of channels from Slack to help
    def update_channels(self):
        self.__channels = {}
        response = self.__client.channels.list(True).body
        for channel in response['channels']:
            self.__channels[channel['name']] = channel['id']
        response = self.__client.groups.list().body
        for channel in response['groups']:
            self.__channels[channel['name']] = channel['id']
        log.debug("Detected the following Slack channnels: {}" .format(self.__channels))

    # Checks for valid channel, otherwise defaults to general
    def get_channel(self, name):
        channel = SlackAlarm.channel_format(name)
        if channel not in self.__channels:
            log.error("Detected no channel with the name '{}'.".format(channel) +
                      " We will try the default channel '{}' instead.".format(self.__default_channel))
            return self.__default_channel
        return channel

    # Send a message to Slack
    def send_message(self, channel, username, text, icon_url=None, attachments=None):
        args = {
            "channel": self.get_channel(channel),
            "username": username,
            "text": text
        }
        if icon_url is not None:
            args['icon_url'] = icon_url
        if attachments is not None:
            args['attachments'] = attachments
        try_sending(log, self.connect, "Slack", self.__client.chat.post_message, args)

    # Returns a string s that is in proper channel format
    @staticmethod
    def channel_format(name):
        if name[0] == '#':  # Remove # if added
            name = name[1:]
        name = name.replace(u"\u2642", "m").replace(u"\u2640", "f").lower()
        return re.sub("[^_a-z0-9-]+", "", name)

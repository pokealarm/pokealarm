# Standard Library Imports
import logging
import requests
# 3rd Party Imports
# Local Imports
from ..Alarm import Alarm
from ..Utils import parse_boolean, get_static_map_url

log = logging.getLogger('Discord')
try_sending = Alarm.try_sending
replace = Alarm.replace

#####################################################  ATTENTION!  #####################################################
# You DO NOT NEED to edit this file to customize messages for services! Please see the Wiki on the correct way to
# customize services In fact, doing so will likely NOT work correctly with many features included in PokeAlarm.
#                               PLEASE ONLY EDIT IF YOU KNOW WHAT YOU ARE DOING!
#####################################################  ATTENTION!  #####################################################


class DiscordAlarm(Alarm):

    _defaults = {
        'pokemon': {
            'username': "<pkmn>",
            'icon_url': "https://raw.githubusercontent.com/kvangent/PokeAlarm/master/icons/<pkmn_id>.png",
            'title': "A wild <pkmn> has appeared!",
            'url': "<gmaps>",
            'body': "Available until <24h_time> (<time_left>)."
        },
        'pokestop': {
            'username': "Pokestop",
            'icon_url': "https://raw.githubusercontent.com/kvangent/PokeAlarm/master/icons/pokestop.png",
            'title': "Someone has placed a lure on a Pokestop!",
            'url': "<gmaps>",
            'body': "Lure will expire at <24h_time> (<time_left>)."
        },
        'gym': {
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
        self.__map = settings.get('map', {})
        self.__statup_list = settings.get('startup_list', "true")

        # Set Alerts
        self.__pokemon = self.set_alert(settings.get('pokemon', {}), self._defaults['pokemon'])
        self.__pokestop = self.set_alert(settings.get('pokestop', {}), self._defaults['pokestop'])
        self.__gym = self.set_alert(settings.get('gym', {}), self._defaults['gym'])

        # Connect and send startup messages
        if parse_boolean(self.__startup_message):
            args = {
                'api_key': self.__api_key,
                'username': 'PokeAlarm',
                'content': 'PokeAlarm activated! We will alert this channel about pokemon.'
            }
            self.send_webhook(**args)
        log.info("Discord Alarm initialized.")

    # Establish connection with Discord
    def connect(self):
        pass

    # Set the appropriate settings for each alert
    def set_alert(self, settings, default):
        alert = {
            'api_key': settings.get('api_key', self.__api_key),
            'username': settings.get('username', default['username']),
            'icon_url': settings.get('icon_url', default['icon_url']),
            'title': settings.get('title', default['title']), 'url': settings.get('url', default['url']),
            'body': settings.get('body', default['body']),
            'map': get_static_map_url(settings.get('map', self.__map))
        }
        return alert

    # Send Alert to Discord
    def send_alert(self, alert, info):
        args = {
            'api_key': alert['api_key'],
            'username': replace(alert['username'], info),
            'title': replace(alert['title'], info),
            'url': replace(alert['url'], info),
            'description': replace(alert['body'], info),
            'thumbnail': replace(alert['icon_url'], info),
            'attachments': replace(alert['map'], {'lat': info['lat'], 'lng': info['lng']})
        }
        try_sending(log, self.connect, "Discord", self.send_webhook, args)

    def send_webhook(self, **args):
        log.debug(args)
        webhook_url = args.pop('api_key')
        if 'content' in args:
            data = {
                'username': args['username'],
                'content': args['content']
            }
        else:
            data = {
                'username': args['username'],
                'embeds': [{
                    'title': args['title'],
                    'url': args['url'],
                    'description': args['description'],
                    'thumbnail': {'url': args['thumbnail']},
                    'image': {'url': args['attachments']}
                }]
            }
        try:
            requests.post(webhook_url, json=data, timeout=(None, 1))
        except requests.exceptions.ReadTimeout:
            log.debug('Response timeout on webhook endpoint %s', self.__api_key)
        except requests.exceptions.RequestException as e:
            log.debug("Discord error was found: \n{}".format(e))

    # Trigger an alert based on Pokemon info
    def pokemon_alert(self, pokemon_info):
        self.send_alert(self.__pokemon, pokemon_info)

    # Trigger an alert based on Pokestop info
    def pokestop_alert(self, pokestop_info):
        self.send_alert(self.__pokestop, pokestop_info)

    # Trigger an alert based on Pokestop info
    def gym_alert(self, gym_info):
        self.send_alert(self.__gym, gym_info)

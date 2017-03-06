# Standard Library Imports
import logging
import requests
import sys
import json
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
            'icon_url': "https://raw.githubusercontent.com/kvangent/PokeAlarm/master/icons/gym_<team_id>.png",
            'title': "A Team <old_team> gym has fallen!",
            'url': "<gmaps>",
            'body': "It is now controlled by <new_team>."
        }
    }

    # Gather settings and create alarm
    def __init__(self, settings):
        # Required Parameters
        if 'webhook_url' in settings:
            self.__webhook_url = settings.pop('webhook_url')
        else:
            log.error("The parameter 'webhook_url' is REQUIRED for 'Discord' alarm type. Please correct this and relaunch.")
            sys.exit(1)

        # Optional Alarm Parameters
        self.__startup_message = parse_boolean(settings.pop('startup_message', "True"))
        self.__map = settings.pop('map', {})  # default for the rest of the alerts

        # Set Alert Parameters
        self.__pokemon = self.set_alert(settings.pop('pokemon', {}), self._defaults['pokemon'])
        self.__pokestop = self.set_alert(settings.pop('pokestop', {}), self._defaults['pokestop'])
        self.__gym = self.set_alert(settings.pop('gym', {}), self._defaults['gym'])

        # Catch WRONG Parameters
        if(len(settings) > 0):
            log.error("Unknown parameters found at Alarm level in 'Discord' alarm: ")
            log.error(settings.keys())
            log.error("Please consult the Discord documentation for proper values")
            sys.exit(1)

        self.startup_message()


    # (Re)connect with Discord
    def connect(self):
        pass

    # Send a message letting the channel know that discord has started
    def startup_message(self):
        if self.__startup_message:
            args = {
                'url': self.__webhook_url,
                'payload':{
                    'username': 'PokeAlarm',
                    'content': 'PokeAlarm activated! We will send alerts to this channel.'
                }
            }
            try_sending(log, self.connect, "Discord", self.send_webhook, args)

    # Set the appropriate settings for each alert
    def set_alert(self, settings, default):
        alert = {
            'webhook_url': settings.pop('webhook_url', self.__webhook_url),
            'username': settings.pop('username', default['username']),
            'icon_url': settings.pop('icon_url', default['icon_url']),
            'title': settings.pop('title', default['title']),
            'url': settings.pop('url', default['url']),
            'body': settings.pop('body', default['body']),
            'map' : get_static_map_url(settings.get('map', self.__map))
        }
        return alert

    # Send Alert to Discord
    def send_alert(self, alert, info):
        log.debug("Attempting to send notification to discord.")
        payload = {
            'username': replace(alert['username'], info),
            'embeds': [{
                'title': replace(alert['title'], info),
                'url': replace(alert['url'], info),
                'description': replace(alert['body'], info),
                'thumbnail': {'url':replace(alert['icon_url'], info)},
                'image': {'url': replace(alert['map'], {'lat': info['lat'], 'lng': info['lng']})},
            }]
        }
        # log.debug(json.dumps(payload, indent=4, sort_keys=True))
        args = {
            'url': alert['webhook_url'],
            'payload': payload
        }
        try_sending(log, self.connect, "Discord", self.send_webhook, args)

    # Trigger an alert based on Pokemon info
    def pokemon_alert(self, pokemon_info):
        self.send_alert(self.__pokemon, pokemon_info)

    # Trigger an alert based on Pokestop info
    def pokestop_alert(self, pokestop_info):
        self.send_alert(self.__pokestop, pokestop_info)

    # Trigger an alert based on Pokestop info
    def gym_alert(self, gym_info):
        self.send_alert(self.__gym, gym_info)

    def send_webhook(self, url, payload):
        resp = requests.post(url, json=payload, timeout=(None, 3))
        log.debug("Request completed with return code {}".format(resp.status_code))
        if resp.ok is not True:
            raise requests.exceptions.RequestException("Response received {}, expected 200.".format(resp.status_code))

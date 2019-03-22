# Standard Library Imports
import requests

# 3rd Party Imports
import itertools
# Local Imports
from PokeAlarm.Alarms import Alarm
from PokeAlarm.Utils import parse_boolean, get_static_map_url, \
    reject_leftover_parameters, require_and_remove_key, get_image_url, \
    get_static_weather_map_url

try_sending = Alarm.try_sending
replace = Alarm.replace

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ATTENTION! !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#             ONLY EDIT THIS FILE IF YOU KNOW WHAT YOU ARE DOING!
# You DO NOT NEED to edit this file to customize messages! Please ONLY EDIT the
#     the 'alarms.json'. Failing to do so can cause other feature to break!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ATTENTION! !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


class DiscordAlarm(Alarm):

    _defaults = {
        'monsters': {
            'username': "<mon_name>",
            'content': "",
            'icon_url': get_image_url(
                "regular/monsters/<mon_id_3>_<form_id_3>.png"),
            'avatar_url': get_image_url(
                "regular/monsters/<mon_id_3>_<form_id_3>.png"),
            'title': "A wild <mon_name> has appeared!",
            'url': "<gmaps>",
            'body': "Available until <24h_time> (<time_left>)."
        },
        'stops': {
            'username': "Pokestop",
            'content': "",
            'icon_url': get_image_url("regular/stop/ready.png"),
            'avatar_url': get_image_url("regular/stop/ready.png"),
            'title': "Someone has placed a lure on a Pokestop!",
            'url': "<gmaps>",
            'body': "Lure will expire at <24h_time> (<time_left>)."
        },
        'gyms': {
            'username': "<new_team> Gym Alerts",
            'content': "",
            'icon_url': get_image_url("regular/gyms/<new_team_id>.png"),
            'avatar_url': get_image_url("regular/gyms/<new_team_id>.png"),
            'title': "A Team <old_team> gym has fallen!",
            'url': "<gmaps>",
            'body': "It is now controlled by <new_team>."
        },
        'eggs': {
            'username': "Egg",
            'content': "",
            'icon_url': get_image_url("regular/eggs/<egg_lvl>.png"),
            'avatar_url': get_image_url("regular/eggs/<egg_lvl>.png"),
            'title': "Raid is incoming!",
            'url': "<gmaps>",
            'body': "A level <egg_lvl> raid will hatch at "
                    "<24h_hatch_time> (<hatch_time_left>)."
        },
        'raids': {
            'username': "Raid",
            'content': "",
            'icon_url': get_image_url("regular/monsters/<mon_id_3>_000.png"),
            'avatar_url': get_image_url("regular/monsters/<mon_id_3>_000.png"),
            'title': "Level <raid_lvl> raid is available against <mon_name>!",
            'url': "<gmaps>",
            'body': "The raid is available until "
                    "<24h_raid_end> (<raid_time_left>)."
        },
        'weather': {
            'username': "Weather",
            'content': "",
            "icon_url": get_image_url("regular/weather/<weather_id_3>"
                                      "_<day_or_night_id_3>.png"),
            "avatar_url": get_image_url("regular/weather/<weather_id_3>"
                                        "_<day_or_night_id_3>.png"),
            "title": "The weather has changed!",
            "url": "<gmaps>",
            "body": "The weather around <lat>,<lng> has changed to <weather>!"
        },
        'quests': {
            'username': "Quest",
            'content': "",
            'icon_url': get_image_url("regular/quest/<type_id>.png"),
            'avatar_url': get_image_url("regular/quest/<type_id>.png"),
            'title': "New Quest Found!",
            'url': "<gmaps>",
            'body': "Quest will expire in <time_remaining>"
        }
    }

    # Gather settings and create alarm
    def __init__(self, mgr, settings, max_attempts, static_map_key):
        self._log = mgr.get_child_logger("alarms")
        # Required Parameters
        self.__webhook_url = require_and_remove_key(
            'webhook_url', settings, "'Discord' type alarms.")
        self.__max_attempts = max_attempts

        # Optional Alarm Parameters
        self.__startup_message = parse_boolean(
            settings.pop('startup_message', "True"))
        self.__disable_embed = parse_boolean(
            settings.pop('disable_embed', "False"))
        self.__avatar_url = settings.pop('avatar_url', "")
        self.__map = settings.pop('map', {})
        self.__static_map_key = itertools.cycle(static_map_key)

        # Set Alert Parameters
        self.__monsters = self.create_alert_settings(
            settings.pop('monsters', {}),
            self._defaults['monsters'], 'monsters')
        self.__stops = self.create_alert_settings(
            settings.pop('stops', {}), self._defaults['stops'], 'stops')
        self.__gyms = self.create_alert_settings(
            settings.pop('gyms', {}), self._defaults['gyms'], 'gyms')
        self.__eggs = self.create_alert_settings(
            settings.pop('eggs', {}), self._defaults['eggs'], 'eggs')
        self.__raids = self.create_alert_settings(
            settings.pop('raids', {}), self._defaults['raids'], 'raids')
        self.__weather = self.create_alert_settings(
            settings.pop('weather', {}), self._defaults['weather'], 'weather')
        self.__quest = self.create_alert_settings(
            settings.pop('quest', {}), self._defaults['quest'], 'quest')

        # Warn user about leftover parameters
        reject_leftover_parameters(settings, "'Alarm level in Discord alarm.")

        self._log.info("Discord Alarm has been created!")

    # (Re)connect with Discord
    def connect(self):
        pass

    # Send a message letting the channel know that this alarm has started
    def startup_message(self):
        if self.__startup_message:
            args = {
                'url': self.__webhook_url,
                'payload': {
                    'username': 'PokeAlarm',
                    'content': 'PokeAlarm activated!'
                }
            }
            try_sending(self._log, self.connect, "Discord",
                        self.send_webhook, args, self.__max_attempts)
            self._log.info("Startup message sent!")

    # Set the appropriate settings for each alert
    def create_alert_settings(self, settings, default, kind):
        if kind == 'weather':
            static_map = get_static_weather_map_url(
                settings.pop('map', self.__map))
        else:
            static_map = get_static_map_url(
                settings.pop('map', self.__map))
        alert = {
            'webhook_url': settings.pop('webhook_url', self.__webhook_url),
            'username': settings.pop('username', default['username']),
            'avatar_url': settings.pop('avatar_url', default['avatar_url']),
            'disable_embed': parse_boolean(
                settings.pop('disable_embed', self.__disable_embed)),
            'content': settings.pop('content', default['content']),
            'icon_url': settings.pop('icon_url', default['icon_url']),
            'title': settings.pop('title', default['title']),
            'url': settings.pop('url', default['url']),
            'body': settings.pop('body', default['body']),
            'map': static_map
        }

        reject_leftover_parameters(settings, "'Alert level in Discord alarm.")
        return alert

    # Send Alert to Discord
    def send_alert(self, alert, info):
        self._log.debug("Attempting to send notification to Discord.")
        payload = {
            # Usernames are limited to 32 characters
            'username': replace(alert['username'], info)[:32],
            'content': replace(alert['content'], info),
            'avatar_url': replace(alert['avatar_url'], info),
        }
        if alert['disable_embed'] is False:
            payload['embeds'] = [{
                'title': replace(alert['title'], info),
                'url': replace(alert['url'], info),
                'description': replace(alert['body'], info),
                'thumbnail': {'url': replace(alert['icon_url'], info)}
            }]
            if alert['map'] is not None:
                if info.get('alert_type') == 'weather':
                    map_info = {
                        'lat1': info['coords'][0][0],
                        'lng1': info['coords'][0][1],
                        'lat2': info['coords'][1][0],
                        'lng2': info['coords'][1][1],
                        'lat3': info['coords'][2][0],
                        'lng3': info['coords'][2][1],
                        'lat4': info['coords'][3][0],
                        'lng4': info['coords'][3][1],
                        'gkey': next(self.__static_map_key),
                    }
                else:
                    map_info = {
                        'lat': info['lat'],
                        'lng': info['lng'],
                        'gkey': next(self.__static_map_key),
                    }
                payload['embeds'][0]['image'] = {
                    'url': replace(alert['map'], map_info)
                }
        args = {
            'url': replace(alert['webhook_url'], info),
            'payload': payload
        }
        try_sending(self._log, self.connect,
                    "Discord", self.send_webhook, args, self.__max_attempts)

    # Trigger an alert based on Pokemon info
    def pokemon_alert(self, pokemon_info):
        self._log.debug("Pokemon notification triggered.")
        self.send_alert(self.__monsters, pokemon_info)

    # Trigger an alert based on Pokestop info
    def pokestop_alert(self, pokestop_info):
        self._log.debug("Pokestop notification triggered.")
        self.send_alert(self.__stops, pokestop_info)

    # Trigger an alert based on Pokestop info
    def gym_alert(self, gym_info):
        self._log.debug("Gym notification triggered.")
        self.send_alert(self.__gyms, gym_info)

    # Trigger an alert when a raid egg has spawned (UPCOMING raid event)
    def raid_egg_alert(self, raid_info):
        self._log.debug("Raid Egg notification triggered.")
        self.send_alert(self.__eggs, raid_info)

    def raid_alert(self, raid_info):
        self._log.debug("Raid notification triggered.")
        self.send_alert(self.__raids, raid_info)

    # Trigger an alert based on Weather info
    def weather_alert(self, weather_info):
        self._log.debug("Weather notification triggered.")
        self.send_alert(self.__weather, weather_info)

    def quest_alert(self, quest_info):
        self._log.debug("Quest notification triggered.")
        self.send_alert(self.__quests, quest_info)

    # Send a payload to the webhook url
    def send_webhook(self, url, payload):
        self._log.debug(payload)
        resp = requests.post(url, json=payload, timeout=5)
        if resp.ok is True:
            self._log.debug("Notification successful (returned {})".format(
                resp.status_code))
        else:
            self._log.debug("Discord response was {}".format(resp.content))
            raise requests.exceptions.RequestException(
                "Response received {}, webhook not accepted.".format(
                    resp.status_code))

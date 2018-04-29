# Standard Library Imports
import requests
from collections import namedtuple

# 3rd Party Imports

# Local Imports
from PokeAlarm.Alarms import Alarm
from PokeAlarm.Utilities import GenUtils as utils
from PokeAlarm.Utils import require_and_remove_key, get_image_url

# 2 lazy 2 type
try_sending = Alarm.try_sending
replace = Alarm.replace

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ATTENTION! !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#             ONLY EDIT THIS FILE IF YOU KNOW WHAT YOU ARE DOING!
# You DO NOT NEED to edit this file to customize messages! Please ONLY EDIT the
#     the 'alarms.json'. Failing to do so can cause other feature to break!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ATTENTION! !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


class TelegramAlarm(Alarm):

    Alert = namedtuple(
        "Alert", ['bot_token', 'chat_id', 'sticker', 'sticker_url',
                  'sticker_notify', 'message', 'message_notify', 'venue',
                  'venue_notify', 'map', 'map_notify', 'max_attempts',
                  'web_preview'])

    _defaults = {  # No touchy!!! Edit alarms.json!
        'monsters': {
            'message': "*A wild <mon_name> has appeared!*\n"
                       "Available until <24h_time> (<time_left>).",
            'sticker_url': get_image_url(
                "telegram/monsters/<mon_id_3>_<form_id_3>.webp")
        },
        'stops': {
            'message': "*Someone has placed a lure on a Pokestop!*\n"
                       "Lure will expire at <24h_time> (<time_left>).",
            'sticker_url': get_image_url("telegram/stop/ready.webp")
        },
        'gyms': {
            'message': "*A Team <old_team> gym has fallen!*\n"
                       "It is now controlled by <new_team>.",
            'sticker_url': get_image_url("telegram/gyms/<new_team_id>.webp"),
        },
        'eggs': {
            'message': "*A level <egg_lvl> raid is incoming!*\n"
                       "The egg will hatch <24h_hatch_time> "
                       "(<hatch_time_left>).",
            'sticker_url': get_image_url("telegram/eggs/<egg_lvl>.webp")
        },
        'raids': {
            'message': "*A raid is available against <mon_name>!*\n"
                       "The raid is available until <24h_raid_end> "
                       "(<raid_time_left>).",
            'sticker_url':
                get_image_url("telegram/monsters/<mon_id_3>_000.webp")
        },
        'weather': {
            'message': "The weather around <lat>,<lng> has"
                       " changed to <weather>!",
            'sticker_url': get_image_url(
                "telegram/weather/<weather_id_3>_<day_or_night_id_3>.webp")
        }
    }

    # Gather settings and create alarm
    def __init__(self, mgr, settings):
        self._log = mgr.get_child_logger("alarms")

        # Required Parameters
        self._bot_token = require_and_remove_key(
            'bot_token', settings, "'Telegram' type alarms.")
        self._chat_id = require_and_remove_key(
            'chat_id', settings, "'Telegram' type alarms.")

        self._startup_message = self.pop_type(
            settings, 'startup_message', utils.parse_bool, True)

        # Optional Alert Parameters
        alert_defaults = {
            'bot_token': self._bot_token,
            'chat_id': self._chat_id,
            'sticker': self.pop_type(
                settings, 'sticker', utils.parse_bool, True),
            'sticker_notify': self.pop_type(
                settings, 'sticker_notify', utils.parse_bool, False),
            'message_notify': self.pop_type(
                settings, 'message_notify', utils.parse_bool, True),
            'venue': self.pop_type(
                settings, 'venue', utils.parse_bool, False),
            'venue_notify': self.pop_type(
                settings, 'venue_notify', utils.parse_bool, True),
            'map': self.pop_type(
                settings, 'map', utils.parse_bool, True),
            'map_notify': self.pop_type(
                settings, 'map_notify', utils.parse_bool, False),
            'max_attempts': self.pop_type(
                settings, 'max_attempts', int, 3),
            'web_preview': self.pop_type(
                settings, 'web_preview', utils.parse_bool, False)
        }

        # Alert Settings
        self._mon_alert = self.create_alert_settings(
            'monsters', settings, alert_defaults)
        self._stop_alert = self.create_alert_settings(
            'stops', settings, alert_defaults)
        self._gym_alert = self.create_alert_settings(
            'gyms', settings, alert_defaults)
        self._egg_alert = self.create_alert_settings(
            'eggs', settings, alert_defaults)
        self._raid_alert = self.create_alert_settings(
            'raids', settings, alert_defaults)
        self._weather_alert = self.create_alert_settings(
            'weather', settings, alert_defaults)

        # Reject leftover parameters
        for key in settings:
            raise ValueError("'{}' is not a recognized parameter for the Alarm"
                             " level in a Telegram Alarm".format(key))

        self._log.info("Telegram Alarm has been created!")

    # (Re)establishes Telegram connection
    def connect(self):
        pass

    # Set the appropriate settings for each alert
    def create_alert_settings(self, kind, settings, alert_defaults):
        default = TelegramAlarm._defaults[kind]
        default.update(alert_defaults)
        settings = Alarm.pop_type(settings, kind, dict, {})

        alert = TelegramAlarm.Alert(
            bot_token=Alarm.pop_type(
                settings, 'bot_token', unicode, default['bot_token']),
            chat_id=Alarm.pop_type(
                settings, 'chat_id', unicode, default['chat_id']),
            sticker=Alarm.pop_type(
                settings, 'sticker', utils.parse_bool, default['sticker']),
            sticker_url=Alarm.pop_type(
                settings, 'sticker_url', unicode, default['sticker_url']),
            sticker_notify=Alarm.pop_type(
                settings, 'sticker_notify', utils.parse_bool,
                default['sticker_notify']),
            message=Alarm.pop_type(
                settings, 'message', unicode, default['message']),
            message_notify=Alarm.pop_type(
                settings, 'message_notify', utils.parse_bool,
                default['message_notify']),
            venue=Alarm.pop_type(
                settings, 'venue', utils.parse_bool, default['venue']),
            venue_notify=Alarm.pop_type(
                settings, 'venue_notify', utils.parse_bool,
                default['venue_notify']),
            map=Alarm.pop_type(
                settings, 'map', utils.parse_bool, default['map']),
            map_notify=Alarm.pop_type(
                settings, 'map_notify', utils.parse_bool,
                default['map_notify']),
            max_attempts=Alarm.pop_type(
                settings, 'max_attempts', int, default['max_attempts']),
            web_preview=Alarm.pop_type(
                settings, 'web_preview', utils.parse_bool,
                default['web_preview'])
        )

        # Reject leftover parameters
        for key in settings:
            raise ValueError(
                "'{}' is not a recognized parameter for the Alert"
                " level in a Telegram Alarm".format(key))

        return alert

    # Sends a start up message on Telegram
    def startup_message(self):
        if self._startup_message:
            self.send_message(
                self._bot_token, self._chat_id, "PokeAlarm activated!")
            self._log.info("Startup message sent!")

    # Generic Telegram Alert
    def generic_alert(self, alert, dts):
        bot_token = replace(alert.bot_token, dts)
        chat_id = replace(alert.chat_id, dts)
        message = replace(alert.message, dts)
        lat, lng = dts['lat'], dts['lng']
        max_attempts = alert.max_attempts
        sticker_url = replace(alert.sticker_url, dts)
        self._log.debug(sticker_url)
        # Send Sticker
        if alert.sticker and sticker_url is not None:
            self.send_sticker(bot_token, chat_id, sticker_url, max_attempts)

        # Send Venue
        if alert.venue:
            self.send_venue(
                bot_token, chat_id, lat, lng, message, max_attempts)
            return  # Don't send message or map

        # Send Message
        self.send_message(bot_token, chat_id, replace(message, dts),
                          web_preview=alert.web_preview)

        # Send Map
        if alert.map:
            self.send_location(bot_token, chat_id, lat, lng, max_attempts)

    # Trigger an alert based on Pokemon info
    def pokemon_alert(self, mon_dts):
        self.generic_alert(self._mon_alert, mon_dts)

    # Trigger an alert based on Pokestop info
    def pokestop_alert(self, stop_dts):
        self.generic_alert(self._stop_alert, stop_dts)

    # Trigger an alert based on Pokestop info
    def gym_alert(self, gym_dts):
        self.generic_alert(self._gym_alert, gym_dts)

    # Trigger an alert when a raid egg has spawned (UPCOMING raid event)
    def raid_egg_alert(self, egg_dts):
        self.generic_alert(self._egg_alert, egg_dts)

    # Trigger an alert based on Raid info
    def raid_alert(self, raid_dts):
        self.generic_alert(self._raid_alert, raid_dts)

    # Trigger an alert based on Weather info
    def weather_alert(self, weather_dts):
        self.generic_alert(self._weather_alert, weather_dts)

    def send_sticker(self, token, chat_id, sticker_url,
                     max_attempts=3, notify=False):
        args = {
            'url': "https://api.telegram.org/bot{}/sendSticker".format(token),
            'payload': {
                'chat_id': chat_id,
                'sticker': sticker_url,
                'disable_notification': not notify
            }
        }
        try_sending(
            self._log, self.connect, "Telegram (STKR)", self.send_webhook,
            args, max_attempts)

    def send_message(self, token, chat_id, message,
                     max_attempts=3, notify=True, web_preview=False):
        args = {
            'url': "https://api.telegram.org/bot{}/sendMessage".format(token),
            'payload': {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'Markdown',
                'disable_web_page_preview': not web_preview,
                'disable_notification': not notify
            }
        }
        try_sending(
            self._log, self.connect, "Telegram (MSG)", self.send_webhook,
            args, max_attempts)

    def send_location(self, token, chat_id, lat, lng,
                      max_attempts=3, notify=False):
        args = {
            'url': "https://api.telegram.org/bot{}/sendLocation".format(token),
            'payload': {
                'chat_id': chat_id,
                'latitude': lat,
                'longitude': lng,
                'disable_notification': not notify
            }
        }
        try_sending(
            self._log, self.connect, "Telegram (LOC)", self.send_webhook, args,
            max_attempts)

    def send_venue(self, token, chat_id, lat, lng, message, max_attempts):
        msg = message.split('\n', 1)
        args = {
            'url': "https://api.telegram.org/bot{}/sendVenue".format(
                token),
            'payload': {
                'chat_id': chat_id,
                'latitude': lat,
                'title': msg[0],
                'address': msg[1] if len(msg) > 1 else '',
                'longitude': lng,
                'disable_notification': False
            }
        }
        try_sending(
            self._log, self.connect, "Telegram (VEN)", self.send_webhook, args,
            max_attempts)

    # Send a payload to the webhook url
    def send_webhook(self, url, payload):
        self._log.debug(url)
        self._log.debug(payload)
        resp = requests.post(url, json=payload, timeout=30)
        if resp.ok is True:
            self._log.debug("Notification successful (returned {})".format(
                resp.status_code))
        else:
            self._log.debug("Telegram response was {}".format(resp.content))
            raise requests.exceptions.RequestException(
                "Response received {}, webhook not accepted.".format(
                    resp.status_code))

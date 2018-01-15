# Standard Library Imports
import logging
import requests

# 3rd Party Imports
import telepot

# Local Imports
from PokeAlarm.Alarms import Alarm
from Stickers import sticker_list
from PokeAlarm.Utilities import GenUtils as utils
from PokeAlarm.Utils import require_and_remove_key

log = logging.getLogger('Telegram')

# 2 lazy 2 type
try_sending = Alarm.try_sending
replace = Alarm.replace

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ATTENTION! !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#             ONLY EDIT THIS FILE IF YOU KNOW WHAT YOU ARE DOING!
# You DO NOT NEED to edit this file to customize messages! Please ONLY EDIT the
#     the 'alarms.json'. Failing to do so can cause other feature to break!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ATTENTION! !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


class TelegramAlarm(Alarm):

    class Alert(object):
        """ Class that defines the settings for each alert."""

        def __init__(self, kind, data, alert_defaults):
            default = TelegramAlarm._defaults[kind]
            default.update(alert_defaults)
            settings = Alarm.pop_type(data, kind, dict, {})

            self.stickers = Alarm.pop_type(
                settings, 'stickers', utils.parse_bool, default['stickers'])
            self.stickers_notify = Alarm.pop_type(
                settings, 'stickers_notify', utils.parse_bool,
                default['stickers_notify'])
            self.message = Alarm.pop_type(
                settings, 'message', unicode, default['message'])
            self.message_notify = Alarm.pop_type(
                settings, 'message_notify', utils.parse_bool,
                default['message_notify'])
            self.venue = Alarm.pop_type(
                settings, 'venue', utils.parse_bool, default['venue'])
            self.venue_notify = Alarm.pop_type(
                settings, 'venue_notify', utils.parse_bool,
                default['venue_notify'])
            self.map = Alarm.pop_type(
                settings, 'map', utils.parse_bool, default['map'])
            self.map_notification = Alarm.pop_type(
                settings, 'map_notify', utils.parse_bool,
                default['map_notify'])

            # Reject leftover parameters
            for key in settings:
                raise ValueError(
                    "'{}' is not a recognized parameter for the Alert"
                    " level in a Telegram Alarm".format(key))

    _defaults = {  # No touchy!!! Edit alarms.json!
        'monsters': {
            'message': "__**A wild <mon_name> has appeared!**__\n"
                       "Available until <24h_time> (<time_left>)."
        },
        'stops': {
            'message': "__**Someone has placed a lure on a Pokestop!**__\n"
                       "Lure will expire at <24h_time> (<time_left>)."
        },
        'gyms': {
            'message': "__**A Team <old_team> gym has fallen!**__\n"
                       "It is now controlled by <new_team>."
        },
        'eggs': {
            'message': "__**A level <egg_lvl> raid is incoming!**__\n"
                       "The egg will hatch <24h_hatch_time> "
                       "(<hatch_time_left>)."
        },
        'raids': {
            'message': "__**A raid is available against <mon_name>!**__\n"
                       "The raid is available until <24h_raid_end> "
                       "(<raid_time_left>)."
        }
    }

    # Gather settings and create alarm
    def __init__(self, settings):
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
            'stickers': self.pop_type(
                settings, 'stickers', utils.parse_bool, True),
            'stickers_notify': self.pop_type(
                settings, 'stickers_notify', utils.parse_bool, False),
            'message_notify': self.pop_type(
                settings, 'message_notify', utils.parse_bool, True),
            'venue': self.pop_type(
                settings, 'venue', utils.parse_bool, False),
            'venue_notify': self.pop_type(
                settings, 'venue_notify', utils.parse_bool, True),
            'map': self.pop_type(
                settings, 'map', utils.parse_bool, False),
            'map_notify': self.pop_type(
                settings, 'map_notify', utils.parse_bool, False),
            'max_retries': self.pop_type(
                settings, 'max_retries', int, 3),
        }

        # Alert Settings
        self._mon_alert = TelegramAlarm.Alert(
            'monsters', settings, alert_defaults)
        self._stop_alert = TelegramAlarm.Alert(
            'stops', settings, alert_defaults)
        self._gym_alert = TelegramAlarm.Alert(
            'gyms', settings, alert_defaults)
        self._egg_alert = TelegramAlarm.Alert(
            'eggs', settings, alert_defaults)
        self._raid_alert = TelegramAlarm.Alert(
            'raids', settings, alert_defaults)

        # Reject leftover parameters
        for key in settings:
            raise ValueError("'{}' is not a recognized parameter for the Alarm"
                             " level in a Telegram Alarm".format(key))

        log.info("Telegram Alarm has been created!")

    # (Re)establishes Telegram connection
    def connect(self):
        pass

    # Sends a start up message on Telegram
    def startup_message(self):
        if self._startup_message:
            self.send_message_new(
                self._bot_token, self._chat_id, "PokeAlarm activated!")
            log.info("Startup message sent!")

    # Send Alert to Telegram
    def send_alert(self, alert, info, sticker_id=None):
        if sticker_id:
            self.send_sticker(alert['chat_id'], sticker_id)

        if alert['venue']:
            self.send_venue(alert, info)
        else:
            text = '<b>' + replace(alert['title'], info)\
                   + '</b> \n' + replace(alert['body'], info)
            self.send_message(alert['chat_id'], text)

        if alert['location']:
            self.send_location(alert, info)

    # Trigger an alert based on Pokemon info
    def pokemon_alert(self, pokemon_info):
        if self._mon_alert['stickers']:
            self.send_alert(self._mon_alert, pokemon_info,
                            sticker_list.get(str(pokemon_info['mon_id'])))
        else:
            self.send_alert(self._mon_alert, pokemon_info)

    # Trigger an alert based on Pokestop info
    def pokestop_alert(self, pokestop_info):
        if self._stop_alert['stickers']:
            self.send_alert(self._stop_alert, pokestop_info,
                            sticker_list.get('pokestop'))
        else:
            self.send_alert(self._stop_alert, pokestop_info)

    # Trigger an alert based on Pokestop info
    def gym_alert(self, gym_info):
        if self._gym_alert['stickers']:
            self.send_alert(self._gym_alert, gym_info, sticker_list.get(
                "team{}".format(gym_info['new_team_id'])))
        else:
            self.send_alert(self._gym_alert, gym_info)

    # Trigger an alert when a raid egg has spawned (UPCOMING raid event)
    def raid_egg_alert(self, raid_info):
        if self._raid_alert['stickers'] and raid_info['egg_lvl'] > 0:
            self.send_alert(self._egg_alert, raid_info, sticker_list.get(
                'raid_level_{}'.format(raid_info['egg_lvl'])))
        else:
            self.send_alert(self._egg_alert, raid_info)

    # Trigger an alert based on Raid info
    def raid_alert(self, raid_info):
        if self._raid_alert['stickers'] and raid_info['mon_id'] > 0:
            self.send_alert(self._raid_alert, raid_info, sticker_list.get(
                str(raid_info['mon_id'])))
        else:
            self.send_alert(self._raid_alert, raid_info)

    # Send a message to telegram
    def send_message(self, chat_id, text):
        args = {
            'chat_id': chat_id,
            'text': text,
            'disable_web_page_preview': 'False',
            'disable_notification': 'False',
            'parse_mode': 'HTML'
        }
        try_sending(log, self.connect,
                    "Telegram", self.__client.sendMessage, args)

    # Send a sticker to telegram
    def send_sticker(self, chat_id, sticker_id):
        args = {
            'chat_id': chat_id,
            'sticker': unicode(sticker_id),
            'disable_notification': 'True'
        }
        try_sending(log, self.connect, 'Telegram (sticker)',
                    self.__client.sendSticker, args)

    # Send a venue message to telegram
    def send_venue(self, alert, info):
        args = {
            'chat_id': alert['chat_id'],
            'latitude': info['lat'],
            'longitude': info['lng'],
            'title': replace(alert['title'], info),
            'address': replace(alert['body'], info),
            'disable_notification': 'False'
        }
        try_sending(log, self.connect, "Telegram (venue)",
                    self.__client.sendVenue, args)

    # Send a location message to telegram
    def send_location(self, alert, info):
        args = {
            'chat_id': alert['chat_id'],
            'latitude': info['lat'],
            'longitude': info['lng'],
            'disable_notification': "{}".format(
                alert['disable_map_notification'])
        }
        try_sending(log, self.connect, "Telegram (location)",
                    self.__client.sendLocation, args)

    def send_sticker_new(self, bot_token, chat_id, sticker_id, max_attempts):
        args = {
            'url':
                "https://api.telegram.org/bot{}/sendSticker".format(bot_token),
            'payload': {
                'chat_id': chat_id,
                'sticker_id': sticker_id,
                'disable_notification': False
            }
        }
        try_sending(
            log, self.connect, "Telegram (STKR)", self.send_webhook, args,
            max_attempts)

    def send_message_new(self, bot_token, chat_id, message, max_attempts=3):
        args = {
            'url':
                "https://api.telegram.org/bot{}/sendMessage".format(bot_token),
            'payload': {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'markdown',
                'disable_web_page_preview': False,
                'disable_notification': False
            }
        }
        try_sending(
            log, self.connect, "Telegram (MSG)", self.send_webhook, args, 
            max_attempts)

    def send_location_new(self, bot_token, chat_id, lat, lng, max_attempts):
        args = {
            'url': "https://api.telegram.org/bot{}/sendLocation".format(
                    bot_token),
            'payload': {
                'chat_id': chat_id,
                'latitude': lat,
                'longitude': lng,
                'disable_notification': True
            }
        }
        try_sending(
            log, self.connect, "Telegram (LOC)", self.send_webhook, args,
            max_attempts)

    def send_venue_new(self, bot_token, chat_id, lat, lng, max_attempts):
        args = {
            'url': "https://api.telegram.org/bot{}/sendVenue".format(
                bot_token),
            'payload': {
                'chat_id': chat_id,
                'latitude': lat,
                'longitude': lng,
                'disable_notification': False
            }
        }
        try_sending(
            log, self.connect, "Telegram (VEN)", self.send_webhook, args,
            max_attempts)

    # Send a payload to the webhook url
    def send_webhook(self, url, payload):
        log.debug(url)
        log.debug(payload)
        resp = requests.post(url, json=payload, timeout=5)
        if resp.ok is True:
            log.debug("Notification successful (returned {})".format(
                resp.status_code))
        else:
            log.debug("Telegram response was {}".format(resp.content))
            raise requests.exceptions.RequestException(
                "Response received {}, webhook not accepted.".format(
                    resp.status_code))

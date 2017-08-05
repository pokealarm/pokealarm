# Standard Library Imports
import logging
# 3rd Party Imports
import telepot
# Local Imports
from ..Alarm import Alarm
from Stickers import sticker_list
from ..Utils import parse_boolean, require_and_remove_key, reject_leftover_parameters

log = logging.getLogger('Telegram')
try_sending = Alarm.try_sending
replace = Alarm.replace


#####################################################  ATTENTION!  #####################################################
# You DO NOT NEED to edit this file to customize messages for services! Please see the Wiki on the correct way to
# customize services In fact, doing so will likely NOT work correctly with many features included in PokeAlarm.
#                               PLEASE ONLY EDIT IF YOU KNOW WHAT YOU ARE DOING!
#####################################################  ATTENTION!  #####################################################


class TelegramAlarm(Alarm):
    _defaults = {
        'pokemon': {
            # 'chat_id': If no default, required
            'title': "A wild <pkmn> has appeared!",
            'body': "Available until <24h_time> (<time_left>)."
        },
        'pokestop': {
            # 'chat_id': If no default, required
            'title': "Someone has placed a lure on a Pokestop!",
            'body': "Lure will expire at <24h_time> (<time_left>)."
        },
        'gym': {
            # 'chat_id': If no default, required
            'title': "A Team <old_team> gym has fallen!",
            'body': "It is now controlled by <new_team>."
        },
        'egg': {
            'title': "A level <raid_level> raid is incoming!",
            'body': "The egg will hatch <begin_24h_time> (<begin_time_left>)."
        },
        'raid': {
            'title': "A raid is available against <pkmn>!",
            'body': "The raid is available until <24h_time> (<time_left>)."
        }
    }

    # Gather settings and create alarm
    def __init__(self, settings):
        # Required Parameters
        self.__bot_token = require_and_remove_key('bot_token', settings, "'Telegram' type alarms.")
        self.__chat_id = require_and_remove_key('chat_id', settings, "'Telegram' type alarms.")
        self.__client = None

        # Optional Alarm Parameters
        self.__venue = parse_boolean(settings.pop('venue', "False"))
        self.__location = parse_boolean(settings.pop('location', "True"))
        self.__stickers = parse_boolean(settings.pop('stickers', 'True'))
        self.__disable_map_notification = parse_boolean(settings.pop('disable_map_notification', "True"))
        self.__startup_message = parse_boolean(settings.pop('startup_message', "True"))

        # Optional Alert Parameters
        self.__pokemon = self.create_alert_settings(settings.pop('pokemon', {}), self._defaults['pokemon'])
        self.__pokestop = self.create_alert_settings(settings.pop('pokestop', {}), self._defaults['pokestop'])
        self.__gym = self.create_alert_settings(settings.pop('gym', {}), self._defaults['gym'])
        self.__egg = self.create_alert_settings(settings.pop('egg', {}), self._defaults['egg'])
        self.__raid = self.create_alert_settings(settings.pop('raid', {}), self._defaults['raid'])

        #  Warn user about leftover parameters
        reject_leftover_parameters(settings, "'Alarm level in Telegram alarm.")

        log.info("Telegram Alarm has been created!")

    # (Re)establishes Telegram connection
    def connect(self):
        self.__client = telepot.Bot(self.__bot_token)

    # Sends a start up message on Telegram
    def startup_message(self):
        if self.__startup_message:
            self.send_message(self.__chat_id, "PokeAlarm activated!")
            log.info("Startup message sent!")

    # Set the appropriate settings for each alert
    def create_alert_settings(self, settings, default):
        alert = {
            'chat_id': settings.pop('chat_id', self.__chat_id),
            'title': settings.pop('title', default['title']),
            'body': settings.pop('body', default['body']),
            'venue': parse_boolean(settings.pop('venue', self.__venue)),
            'location': parse_boolean(settings.pop('location', self.__location)),
            'disable_map_notification': parse_boolean(
                settings.pop('disable_map_notification', self.__disable_map_notification)),
            'stickers': parse_boolean(settings.pop('stickers', self.__stickers))
        }
        reject_leftover_parameters(settings, "'Alert level in Telegram alarm.")
        return alert

    # Send Alert to Telegram
    def send_alert(self, alert, info, sticker_id=None):
        if sticker_id:
            self.send_sticker(alert['chat_id'], sticker_id)

        if alert['venue']:
            self.send_venue(alert, info)
        else:
            text = '<b>' + replace(alert['title'], info) + '</b> \n' + replace(alert['body'], info)
            self.send_message(alert['chat_id'], text)

        if alert['location']:
            self.send_location(alert, info)

    # Trigger an alert based on Pokemon info
    def pokemon_alert(self, pokemon_info):
        if self.__pokemon['stickers']:
            self.send_alert(self.__pokemon, pokemon_info, sticker_list.get(str(pokemon_info['pkmn_id'])))
        else:
            self.send_alert(self.__pokemon, pokemon_info)

    # Trigger an alert based on Pokestop info
    def pokestop_alert(self, pokestop_info):
        if self.__pokestop['stickers']:
            self.send_alert(self.__pokestop, pokestop_info, sticker_list.get('pokestop'))
        else:
            self.send_alert(self.__pokestop, pokestop_info)

    # Trigger an alert based on Pokestop info
    def gym_alert(self, gym_info):
        if self.__gym['stickers']:
            self.send_alert(self.__gym, gym_info, sticker_list.get("team{}".format(gym_info['new_team_id'])))
        else:
            self.send_alert(self.__gym, gym_info)

    # Trigger an alert when a raid egg has spawned (UPCOMING raid event)
    def raid_egg_alert(self, raid_info):
        if self.__raid['stickers'] and raid_info['raid_level'] > 0:
            self.send_alert(self.__egg, raid_info, sticker_list.get('raid_level_{}'.format(raid_info['raid_level'])))
        else:
            self.send_alert(self.__egg, raid_info)

    # Trigger an alert based on Raid info
    def raid_alert(self, raid_info):
        if self.__raid['stickers'] and raid_info['pkmn_id'] > 0:
            self.send_alert(self.__raid, raid_info, sticker_list.get(str(raid_info['pkmn_id'])))
        else:
            self.send_alert(self.__raid, raid_info)

    # Send a message to telegram
    def send_message(self, chat_id, text):
        args = {
            'chat_id': chat_id,
            'text': text,
            'disable_web_page_preview': 'False',
            'disable_notification': 'False',
            'parse_mode': 'HTML'
        }
        try_sending(log, self.connect, "Telegram", self.__client.sendMessage, args)

    # Send a sticker to telegram
    def send_sticker(self, chat_id, sticker_id):
        args = {
            'chat_id': chat_id,
            'sticker': unicode(sticker_id),
            'disable_notification': 'True'
        }
        try_sending(log, self.connect, 'Telegram (sticker)', self.__client.sendSticker, args)

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
        try_sending(log, self.connect, "Telegram (venue)", self.__client.sendVenue, args)

    # Send a location message to telegram
    def send_location(self, alert, info):
        args = {
            'chat_id': alert['chat_id'],
            'latitude': info['lat'],
            'longitude': info['lng'],
            'disable_notification': "{}".format(alert['disable_map_notification'])
        }
        try_sending(log, self.connect, "Telegram (location)", self.__client.sendLocation, args)

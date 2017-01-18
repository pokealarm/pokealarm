# Standard Library Imports
import logging
# 3rd Party Imports
import telepot
# Local Imports
from ..Alarm import Alarm
from Stickers import sticker_list
from ..Utils import parse_boolean

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
        }
    }

    # Gather settings and create alarm
    def __init__(self, settings):
        # Service Info
        self.__bot_token = settings['bot_token']
        self.__chat_id = settings.get('chat_id')
        self.__venue = settings.get('venue', "False")
        self.__location = settings.get('location', "True")
        self.__disable_map_notification = settings.get('disable_map_notification', "True")
        self.__startup_message = settings.get('startup_message', "True")
        self.__startup_list = settings.get('startup_list', "True")
        self.__stickers = parse_boolean(settings.get('stickers', 'True'))

        # Set Alerts
        self.__pokemon = self.set_alert(settings.get('pokemon', {}), self._defaults['pokemon'])
        log.debug(self.__pokemon)
        self.__pokestop = self.set_alert(settings.get('pokestop', {}), self._defaults['pokestop'])
        log.debug(self.__pokestop)
        self.__gym = self.set_alert(settings.get('gym', {}), self._defaults['gym'])
        log.debug(self.__gym)

        # Connect and send startup messages
        self.__client = None
        self.connect()
        if parse_boolean(self.__startup_message):
            self.__client.sendMessage(self.__pokemon['chat_id'],
                                      'PokeAlarm activated! We will alert this chat about pokemon.')
        log.info("Telegram Alarm intialized.")

    # (Re)establishes Telegram connection
    def connect(self):
        self.__client = telepot.Bot(self.__bot_token)

    # Set the appropriate settings for each alert
    def set_alert(self, settings, default):
        alert = {
            'chat_id': settings.get('chat_id', self.__chat_id),
            'title': settings.get('title', default['title']),
            'body': settings.get('body', default['body']),
            'venue': parse_boolean(settings.get('venue', self.__venue)),
            'location': parse_boolean(settings.get('location', self.__location)),
            'disable_map_notification': parse_boolean(
             settings.get('disable_map_notification', self.__disable_map_notification)),
            'stickers': parse_boolean(settings.get('stickers', self.__stickers))
        }
        return alert

    # Send Alert to Telegram
    def send_alert(self, alert, info, sticker_id=None):
        if sticker_id:
            stickerargs = {
                'chat_id': alert['chat_id'],
                'sticker': sticker_id,
                'disable_notification': 'True'
            }
            try_sending(log, self.connect, 'Telegram (sticker)', self.__client.sendSticker, stickerargs)

        if alert['venue']:
            args = {
                'chat_id': alert['chat_id'],
                'latitude': info['lat'],
                'longitude': info['lng'],
                'title': replace(alert['title'], info),
                'address': replace(alert['body'], info),
                'disable_notification': 'False'
            }
            try_sending(log, self.connect, "Telegram (venue)", self.__client.sendVenue, args)
        else:
            args = {
                'chat_id': alert['chat_id'],
                'text': '<b>' + replace(alert['title'], info) + '</b> \n' + replace(alert['body'], info),
                'disable_web_page_preview': 'False',
                'disable_notification': 'False',
                'parse_mode':'HTML'
            }
            try_sending(log, self.connect, "Telegram", self.__client.sendMessage, args)
        if alert['location']:
            args = {
                'chat_id': alert['chat_id'],
                'latitude': info['lat'],
                'longitude': info['lng'],
                'disable_notification': "%s" % alert['disable_map_notification']
            }
            try_sending(log, self.connect, "Telegram (loc)", self.__client.sendLocation, args)

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
            self.send_alert(self.__gym, gym_info, sticker_list.get(gym_info['new_team'].lower()))
        else:
            self.send_alert(self.__gym, gym_info)

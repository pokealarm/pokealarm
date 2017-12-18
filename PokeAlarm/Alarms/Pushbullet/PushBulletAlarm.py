# Standard Library Imports
import logging

# 3rd Party Imports
from pushbullet import PushBullet

# Local Imports
from PokeAlarm.Alarms import Alarm
from PokeAlarm.Utils import parse_boolean, require_and_remove_key, \
    reject_leftover_parameters

log = logging.getLogger(__name__)
try_sending = Alarm.try_sending
replace = Alarm.replace


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ATTENTION! !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#             ONLY EDIT THIS FILE IF YOU KNOW WHAT YOU ARE DOING!
# You DO NOT NEED to edit this file to customize messages! Please ONLY EDIT the
#     the 'alarms.json'. Failing to do so can cause other feature to break!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ATTENTION! !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


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
        },
        'egg': {
            'title': "A level <raid_level> raid is incoming!",
            'url': "<gmaps>",
            'body': "The egg will hatch <begin_24h_time> (<begin_time_left>)."
        },
        'raid': {
            'title': "A Raid is available against <pkmn>!",
            'url': "<gmaps>",
            'body': "The raid is available until <24h_time> (<time_left>)."
        }
    }

    # Gather settings and create alarm
    def __init__(self, settings):
        # Required Parameters
        self.__api_key = require_and_remove_key(
            'api_key', settings, "'Pushbullet' type alarms.")
        self.__client = None

        # Optional Alarm Parameters
        self.__startup_message = parse_boolean(
            settings.pop('startup_message', "True"))
        self.__channel = settings.pop('channel', "True")
        self.__sender = None

        # Optional Alert Parameters
        self.__pokemon = self.create_alert_settings(
            settings.pop('pokemon', {}), self._defaults['pokemon'])
        self.__pokestop = self.create_alert_settings(
            settings.pop('pokestop', {}), self._defaults['pokestop'])
        self.__gym = self.create_alert_settings(
            settings.pop('gyms', {}), self._defaults['gym'])
        self.__egg = self.create_alert_settings(
            settings.pop('egg', {}), self._defaults['egg'])
        self.__raid = self.create_alert_settings(
            settings.pop('raid', {}), self._defaults['raid'])

        #  Warn user about leftover parameters
        reject_leftover_parameters(
            settings, "Alarm level in Pushbullet alarm.")

        log.info("Pushbullet Alarm has been created!")

    # Establish connection with Pushbullet
    def connect(self):
        self.__client = PushBullet(self.__api_key)
        self.__sender = self.get_sender(self.__channel)
        self.__pokemon['sender'] = self.get_sender(self.__pokemon['channel'])
        self.__pokestop['sender'] = self.get_sender(self.__pokestop['channel'])
        self.__gym['sender'] = self.get_sender(self.__gym['channel'])
        self.__egg['sender'] = self.get_sender(self.__egg['channel'])
        self.__raid['sender'] = self.get_sender(self.__raid['channel'])

    def startup_message(self):
        if self.__startup_message:
            args = {
                "sender": self.__sender,
                "title": "PokeAlarm activated!",
                "message": "PokeAlarm has successully started!"
            }
            try_sending(log, self.connect, "PushBullet", self.push_note, args)
            log.info("Startup message sent!")

    # Set the appropriate settings for each alert
    def create_alert_settings(self, settings, default):
        alert = {
            'title': settings.pop('title', default['title']),
            'url': settings.pop('url', default['url']),
            'body': settings.pop('body', default['body']),
            'channel': settings.pop('channel', None)
        }
        reject_leftover_parameters(
            settings, "Alert level in Pushbullet alarm.")
        return alert

    # Send Alert to Pushbullet
    def send_alert(self, alert, info):
        args = {
            'sender': alert['sender'],
            'title': replace(alert['title'], info),
            'url': replace(alert['url'], info),
            'body': replace(alert['body'], info)
        }
        try_sending(log, self.connect, "PushBullet", self.push_link, args)

    # Trigger an alert based on Pokemon info
    def pokemon_alert(self, pokemon_info):
        self.send_alert(self.__pokemon, pokemon_info)

    # Trigger an alert based on Pokestop info
    def pokestop_alert(self, pokestop_info):
        self.send_alert(self.__pokestop, pokestop_info)

    # Trigger an alert based on Gym info
    def gym_alert(self, gym_info):
        self.send_alert(self.__gym, gym_info)

    # Trigger an alert when a raid egg has spawned (UPCOMING raid event)
    def raid_egg_alert(self, raid_info):
        self.send_alert(self.__egg, raid_info)

    # Trigger an alert based on Gym info
    def raid_alert(self, raid_info):
        self.send_alert(self.__raid, raid_info)

    # Attempt to get the channel, otherwise default to all devices
    def get_sender(self, channel_tag):
        req_channel = next(
            (channel for channel in self.__client.channels
             if channel.channel_tag == channel_tag), self.__client)
        if req_channel is self.__client and channel_tag is not None:
            log.error("Unable to find channel.Pushing to all devices instead.")
        else:
            log.debug("Setting to channel %s." % channel_tag)
        return req_channel

    # Push a link to the given channel
    def push_link(self, sender, title, url, body):
        sender.push_link(title=title, url=url, body=body)

    # Push a link to the given channel
    def push_note(self, sender, title, message):
        sender.push_note(title, message)

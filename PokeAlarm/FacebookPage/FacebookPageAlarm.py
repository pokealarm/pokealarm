# Standard Library Imports
from datetime import datetime
import logging
# 3rd Party Imports
import facebook
# Local Imports
from ..Alarm import Alarm
from ..Utils import parse_boolean, get_time_as_str, reject_leftover_parameters, require_and_remove_key

log = logging.getLogger(__name__)
try_sending = Alarm.try_sending
replace = Alarm.replace


#####################################################  ATTENTION!  #####################################################
# You DO NOT NEED to edit this file to customize messages for services! Please see the Wiki on the correct way to
# customize services In fact, doing so will likely NOT work correctly with many features included in PokeAlarm.
#                               PLEASE ONLY EDIT IF YOU KNOW WHAT YOU ARE DOING!
#####################################################  ATTENTION!  #####################################################


class FacebookPageAlarm(Alarm):


    _defaults = {
        'pokemon': {
            'message': "A wild <pkmn> has appeared!",
            'image': "https://raw.githubusercontent.com/RocketMap/PokeAlarm/master/icons/<pkmn_id>.png",
            'link': "<gmaps>",
            'name': "<pkmn>",
            'description': "Available until <24h_time> (<time_left>)",
            'caption': None
        },
        'pokestop': {
            'message': "Someone has placed a lure on a Pokestop!",
            'image': "https://raw.githubusercontent.com/RocketMap/PokeAlarm/master/icons/pokestop.png",
            'link': "<gmaps>",
            'name': "Lured Pokestop",
            'description': "Lure will expire at <24h_time> (<time_left>)",
            'caption': None
        },
        'gym': {
            'message': "A Team <old_team> gym has fallen!",
            'image': "https://raw.githubusercontent.com/RocketMap/PokeAlarm/master/icons/gym_<new_team_id>.png",
            'link': "<gmaps>",
            'name': "<old_team> gym fallen",
            'description': "It is now controlled by <new_team>",
            'caption': None
        },
        'egg': {
            'message': "A level <raid_level> raid is upcoming!",
            'image': "https://raw.githubusercontent.com/RocketMap/PokeAlarm/master/icons/egg_<raid_level>.png",
            'link': "<gmaps>",
            'name': 'Egg',
            'description': "The egg will hatch <begin_24h_time> (<begin_time_left>).",
            'caption': None
        },
        'raid': {
            'message': "A Raid is available against <pkmn>!",
            'image': "https://raw.githubusercontent.com/RocketMap/PokeAlarm/master/icons/<pkmn_id>.png",
            'link': "<gmaps>",
            'name': 'Raid',
            'description': "The raid is available until <24h_time> (<time_left>).",
            'caption': None
        }
    }
    # Gather settings and create alarm
    def __init__(self, settings):
        # Required Parameters
        self.__page_access_token = require_and_remove_key('page_access_token', settings, "'FacebookPage' type alarms.")
        self.__client = None

        # Optional Alarm Parameters
        self.__startup_message = parse_boolean(settings.pop('startup_message', "True"))

        # Set Alerts
        self.__pokemon = self.create_alert_settings(settings.pop('pokemon', {}), self._defaults['pokemon'])
        self.__pokestop = self.create_alert_settings(settings.pop('pokestop', {}), self._defaults['pokestop'])
        self.__gym = self.create_alert_settings(settings.pop('gym', {}), self._defaults['gym'])
        self.__egg = self.create_alert_settings(settings.pop('egg', {}), self._defaults['egg'])
        self.__raid = self.create_alert_settings(settings.pop('raid', {}), self._defaults['raid'])

        #  Warn user about leftover parameters
        reject_leftover_parameters(settings, "'Alarm level in FacebookPage alarm.")

        log.info("FacebookPage Alarm has been created!")

    # Establish connection with FacebookPage
    def connect(self):
        self.__client = facebook.GraphAPI(self.__page_access_token)

    # Sends a start up message on Telegram
    def startup_message(self):
        if self.__startup_message:
            timestamps = get_time_as_str(datetime.utcnow())
            self.post_to_wall("{} - PokeAlarm has intialized!".format(timestamps[2]))
            log.info("Startup message sent!")

    # Set the appropriate settings for each alert
    def create_alert_settings(self, settings, default):
        alert = {
            'message': settings.pop('message', default['message']),
            'link': settings.pop('link', default['link']),
            'caption': settings.pop('caption', default['caption']),
            'description': settings.pop('description', default['description']),
            'image': settings.pop('image', default['image']),
            'name': settings.pop('name', default['name'])
        }
        reject_leftover_parameters(settings, "'Alert level in FacebookPage alarm.")
        return alert

    # Post Pokemon Message
    def send_alert(self, alert, info):
        attachment = {"link": replace(alert['link'], info)}
        if alert['caption']:
            attachment['caption'] = replace(alert['caption'], info)
        if alert['description']:
            attachment['description'] = replace(alert['description'], info)
        if alert['image']:
            attachment['picture'] = replace(alert['image'], info)
        if alert['name']:
            attachment['name'] = replace(alert['name'], info)
        self.post_to_wall(
            message=replace(alert['message'], info),
            attachment = attachment
        )

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

    # Trigger an alert based on Raid info
    def raid_alert(self, raid_info):
        self.send_alert(self.__raid, raid_info)

    # Sends a wall post to Facebook
    def post_to_wall(self, message, attachment=None):
        args = {"message": message}
        if attachment is not None:
            args['attachment'] = attachment
        try_sending(log, self.connect, "FacebookPage", self.__client.put_wall_post, args)

# Standard Library Imports
from datetime import datetime

# 3rd Party Imports
import facebook

# Local Imports
from PokeAlarm.Alarms import Alarm
from PokeAlarm.Utils import parse_boolean, get_time_as_str, \
    reject_leftover_parameters, require_and_remove_key, get_image_url

try_sending = Alarm.try_sending
replace = Alarm.replace


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ATTENTION! !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#             ONLY EDIT THIS FILE IF YOU KNOW WHAT YOU ARE DOING!
# You DO NOT NEED to edit this file to customize messages! Please ONLY EDIT the
#     the 'alarms.json'. Failing to do so can cause other feature to break!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ATTENTION! !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


class FacebookPageAlarm(Alarm):

    _defaults = {
        'monsters': {
            'message': "A wild <mon_name> has appeared!",
            'image': get_image_url(
                "regular/monsters/<mon_id_3>_<form_id_3>.png"),
            'link': "<gmaps>",
            'name': "<mon_name>",
            'description': "Available until <24h_time> (<time_left>).",
            'caption': None
        },
        'stops': {
            'message': "Someone has placed a lure on a Pokestop!",
            'image': get_image_url("regular/stop/ready.png"),
            'link': "<gmaps>",
            'name': "Lured Pokestop",
            'description': "Lure will expire at <24h_time> (<time_left>).",
            'caption': None
        },
        'gyms': {
            'message': "A Team <old_team> gym has fallen!",
            'image': get_image_url("regular/gyms/<new_team_id>.png"),
            'link': "<gmaps>",
            'name': "<old_team> gym fallen",
            'description': "It is now controlled by <new_team>.",
            'caption': None
        },
        'eggs': {
            'message': "A level <egg_lvl> raid is upcoming!",
            'image': get_image_url("regular/eggs/<egg_lvl>.png"),
            'link': "<gmaps>",
            'name': 'Egg',
            'description': "A level <egg_lvl> raid will hatch at "
                           "<24h_hatch_time> (<hatch_time_left>).",
            'caption': None
        },
        'raids': {
            'message': "Level <raid_lvl> raid available against <mon_name>!",
            'image': get_image_url(
                "regular/monsters/<mon_id_3>_000.png"),
            'link': "<gmaps>",
            'name': 'Raid',
            'description':
                "The raid is available until <24h_raid_end>"
                " (<raid_time_left>).",
            'caption': None
        },
        'weather': {
            'message': 'The weather has changed!',
            "image": get_image_url("regular/weather/<weather_id_3>"
                                   "_<day_or_night_id_3>.png"),
            "link": "<gmaps>",
            'name': "Weather",
            'description': "The weather around <lat>,<lng>"
                           " has changed to <weather>!",
            'caption': None
        }
    }

    # Gather settings and create alarm
    def __init__(self, mgr, settings):
        self._log = mgr.get_child_logger("alarms")

        # Required Parameters
        self.__page_access_token = require_and_remove_key(
            'page_access_token', settings, "'FacebookPage' type alarms.")
        self.__client = None

        # Optional Alarm Parameters
        self.__startup_message = parse_boolean(
            settings.pop('startup_message', "True"))

        # Set Alerts
        self.__monsters = self.create_alert_settings(
            settings.pop('monsters', {}), self._defaults['monsters'])
        self.__stops = self.create_alert_settings(
            settings.pop('stops', {}), self._defaults['stops'])
        self.__gyms = self.create_alert_settings(
            settings.pop('gyms', {}), self._defaults['gyms'])
        self.__eggs = self.create_alert_settings(
            settings.pop('eggs', {}), self._defaults['eggs'])
        self.__raids = self.create_alert_settings(
            settings.pop('raids', {}), self._defaults['raids'])
        self.__weather = self.create_alert_settings(
            settings.pop('weather', {}), self._defaults['weather'])

        #  Warn user about leftover parameters
        reject_leftover_parameters(
            settings, "Alarm level in FacebookPage alarm.")

        self._log.info("FacebookPage Alarm has been created!")

    # Establish connection with FacebookPage
    def connect(self):
        self.__client = facebook.GraphAPI(self.__page_access_token)

    # Sends a start up message on Facebook
    def startup_message(self):
        if self.__startup_message:
            timestamps = get_time_as_str(datetime.utcnow())
            self.post_to_wall("{} - PokeAlarm has initialized!".format(
                timestamps[2]))
            self._log.info("Startup message sent!")

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
        reject_leftover_parameters(
            settings, "Alert level in FacebookPage alarm.")
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
            attachment=attachment
        )

    # Trigger an alert based on Pokemon info
    def pokemon_alert(self, pokemon_info):
        self.send_alert(self.__monsters, pokemon_info)

    # Trigger an alert based on Pokestop info
    def pokestop_alert(self, pokestop_info):
        self.send_alert(self.__stops, pokestop_info)

    # Trigger an alert based on Gym info
    def gym_alert(self, gym_info):
        self.send_alert(self.__gyms, gym_info)

    # Trigger an alert when a raid egg has spawned (UPCOMING raid event)
    def raid_egg_alert(self, raid_info):
        self.send_alert(self.__eggs, raid_info)

    # Trigger an alert based on Raid info
    def raid_alert(self, raid_info):
        self.send_alert(self.__raids, raid_info)

    # Trigger an alert based on Weather info
    def weather_alert(self, weather_info):
        self.send_alert(self.__weather, weather_info)

    # Sends a wall post to Facebook
    def post_to_wall(self, message, attachment=None):
        args = {"message": message}
        if attachment is not None:
            args['attachment'] = attachment
        try_sending(self._log, self.connect, "FacebookPage",
                    self.__client.put_wall_post, args)

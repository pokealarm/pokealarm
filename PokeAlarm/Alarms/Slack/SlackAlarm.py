# Standard Library Imports
import re

# 3rd Party Imports
from slack import WebClient

# Local Imports
from PokeAlarm.Alarms import Alarm
from PokeAlarm.Utils import (
    parse_boolean,
    get_gmaps_static_url,
    require_and_remove_key,
    reject_leftover_parameters,
    get_image_url,
    sign_gmaps_static_url,
)

try_sending = Alarm.try_sending
replace = Alarm.replace


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ATTENTION! !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#             ONLY EDIT THIS FILE IF YOU KNOW WHAT YOU ARE DOING!
# You DO NOT NEED to edit this file to customize messages! Please ONLY EDIT the
#     the 'alarms.json'. Failing to do so can cause other feature to break!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ATTENTION! !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


class SlackAlarm(Alarm):

    _defaults = {
        "monsters": {
            "username": "<mon_name>",
            "icon_url": get_image_url("regular/monsters/<mon_id_3>_<form_id_3>.png"),
            "display_icon_url": get_image_url(
                "regular/monsters/<display_mon_id_3>_<display_form_id_3>.png"
            ),
            "title": "A wild <mon_name> has appeared!",
            "url": "<gmaps>",
            "body": "Available until <24h_time> (<time_left>).",
        },
        "stops": {
            "username": "Pokestop",
            "icon_url": get_image_url("regular/stop/<lure_type_id_3>.png"),
            "title": "Someone has placed a lure on a Pokestop!",
            "url": "<gmaps>",
            "body": "Lure will expire at <24h_time> (<time_left>).",
        },
        "gyms": {
            "username": "<new_team> Gym Alerts",
            "icon_url": get_image_url("regular/gyms/<new_team_id>.png"),
            "title": "A Team <old_team> gym has fallen!",
            "url": "<gmaps>",
            "body": "It is now controlled by <new_team>.",
        },
        "eggs": {
            "username": "Egg",
            "icon_url": get_image_url("regular/eggs/<egg_lvl>.png"),
            "title": "A level <egg_lvl> raid is incoming!",
            "url": "<gmaps>",
            "body": "The egg will hatch <24h_hatch_time> (<hatch_time_left>).",
        },
        "raids": {
            "username": "<mon_name> Raid",
            "icon_url": get_image_url("regular/monsters/<mon_id_3>_<form_id_3>.png"),
            "title": "Level <raid_lvl> raid is available against <mon_name>!",
            "url": "<gmaps>",
            "body": "The raid is available until <24h_raid_end> (<raid_time_left>).",
        },
        "weather": {
            "username": "Weather",
            "icon_url": get_image_url(
                "regular/weather/<weather_id_3>_<day_or_night_id_3>.png"
            ),
            "title": "The weather has changed!",
            "url": "<gmaps>",
            "body": "The weather around <lat>,<lng> has changed to <weather>!",
        },
        "quests": {
            "username": "Quest",
            "icon_url": get_image_url("regular/<quest_image>.png"),
            "title": "New Quest Found!",
            "url": "<gmaps>",
            "body": "New quest for <reward>\nTask: <quest_task>",
        },
        "invasions": {
            "username": "Invasion",
            "content": "",
            "icon_url": get_image_url("regular/invasions/<grunt_id_3>.png"),
            "title": "This Pokestop has been invaded by Team Rocket!",
            "url": "<gmaps>",
            "body": "Invasion will expire at <24h_time> (<time_left>).",
        },
    }

    # Gather settings and create alarm
    def __init__(self, mgr, settings, static_map_key, signing_secret_key):
        self._log = mgr.get_child_logger("alarms")

        # Required Parameters
        self.__api_key = require_and_remove_key(
            "api_key", settings, "'Slack' type alarms."
        )
        self.__default_channel = self.channel_format(
            require_and_remove_key("channel", settings, "'Slack' type alarms.")
        )
        self.__client = None
        self.__channels = {}

        # Optional Alarm Parameters
        self.__startup_message = parse_boolean(settings.pop("startup_message", "True"))
        self.__startup_text = settings.pop("startup_text", "")
        self.__map = settings.pop("map", {})
        self.__static_map_key = static_map_key
        self.__signing_secret_key = signing_secret_key

        # Optional Alert Parameters
        self.__pokemon = self.create_alert_settings(
            settings.pop("monsters", {}), self._defaults["monsters"]
        )
        self.__pokestop = self.create_alert_settings(
            settings.pop("stops", {}), self._defaults["stops"]
        )
        self.__gym = self.create_alert_settings(
            settings.pop("gyms", {}), self._defaults["gyms"]
        )
        self.__egg = self.create_alert_settings(
            settings.pop("eggs", {}), self._defaults["eggs"]
        )
        self.__raid = self.create_alert_settings(
            settings.pop("raids", {}), self._defaults["raids"]
        )
        self.__weather = self.create_alert_settings(
            settings.pop("weather", {}), self._defaults["weather"]
        )
        self.__quests = self.create_alert_settings(
            settings.pop("quests", {}), self._defaults["quests"]
        )
        self.__invasions = self.create_alert_settings(
            settings.pop("invasions", {}), self._defaults["invasions"]
        )

        # Warn user about leftover parameters
        reject_leftover_parameters(settings, "'Alarm level in Slack alarm.")

        self._log.info("Slack Alarm has been created!")

    # Establish connection with Slack
    def connect(self):
        self.__client = WebClient(self.__api_key)
        self.update_channels()

    # Send a message letting the channel know that this alarm started
    def startup_message(self):
        if self.__startup_message:
            self.send_message(
                self.__default_channel,
                username="PokeAlarm",
                text=(
                    "PokeAlarm activated!"
                    if self.__startup_text == ""
                    else self.__startup_text
                ),
            )
            self._log.info("Startup message sent!")

    # Set the appropriate settings for each alert
    def create_alert_settings(self, settings, default):
        map = settings.pop("map", self.__map)
        use_display_icon = settings.pop("use_display_icon", False)
        alert = {
            "channel": settings.pop("channel", self.__default_channel),
            "username": settings.pop("username", default["username"]),
            "icon_url": settings.pop(
                "icon_url",
                default["display_icon_url"]
                if use_display_icon
                else default["icon_url"],
            ),
            "title": settings.pop("title", default["title"]),
            "url": settings.pop("url", default["url"]),
            "body": settings.pop("body", default["body"]),
            "map": map
            if isinstance(map, str)
            else get_gmaps_static_url(map, self.__static_map_key),
        }
        reject_leftover_parameters(settings, "'Alert level in Slack alarm.")
        return alert

    # Send Alert to Slack
    def send_alert(self, alert, info):
        attachments = None
        if alert["map"] is not None:
            static_map_url = ""
            if not isinstance(alert["map"], str):
                coords = {"lat": info["lat"], "lng": info["lng"]}
                static_map_url = replace(alert["map"], coords)
            else:
                static_map_url = replace(alert["map"], info)
                if self.__signing_secret_key is not None:
                    static_map_url = sign_gmaps_static_url(
                        static_map_url, self.__signing_secret_key
                    )

            attachments = [{"fallback": "Map_Preview", "image_url": static_map_url}]

        self.send_message(
            channel=replace(alert["channel"], info),
            username=replace(alert["username"], info),
            text=f'<{replace(alert["url"], info)}|{replace(alert["title"], info)}> - {replace(alert["body"], info)}',
            icon_url=replace(alert["icon_url"], info),
            attachments=attachments,
        )

    # Trigger an alert based on Pokemon info
    def pokemon_alert(self, pokemon_info):
        self.send_alert(self.__pokemon, pokemon_info)

    # Trigger an alert based on Pokestop info
    def pokestop_alert(self, pokestop_info):
        self.send_alert(self.__pokestop, pokestop_info)

    # Trigger an alert based on Pokestop info
    def gym_alert(self, gym_info):
        self.send_alert(self.__gym, gym_info)

    # Trigger an alert when a raid egg has spawned (UPCOMING raid event)
    def raid_egg_alert(self, raid_info):
        self.send_alert(self.__egg, raid_info)

    # Trigger an alert based on Gym info
    def raid_alert(self, raid_info):
        self.send_alert(self.__raid, raid_info)

    # Trigger an alert based on Weather info
    def weather_alert(self, weather_info):
        self.send_alert(self.__weather, weather_info)

    # Trigger quest alert
    def quest_alert(self, quest_info):
        self.send_alert(self.__quests, quest_info)

    # Trigger invasion alert
    def invasion_alert(self, invasion_info):
        self.send_alert(self.__invasions, invasion_info)

    # Get a list of channels from Slack to help
    def update_channels(self):
        self.__channels = {}
        response = self.__client.conversations_list()
        for channel in response.data["channels"]:
            self.__channels[channel["name"]] = channel["id"]
        self._log.debug(f"Detected the following Slack channnels: {self.__channels}")

    # Checks for valid channel, otherwise defaults to general
    def get_channel(self, name):
        channel = SlackAlarm.channel_format(name)
        if channel not in self.__channels:
            self._log.error(
                f"Detected no channel with the name '{channel}'. Trying the default channel '{self.__default_channel}' instead."
            )
            return self.__default_channel
        return channel

    # Send a message to Slack
    def send_message(self, channel, username, text, icon_url=None, attachments=None):
        args = {
            "channel": self.get_channel(channel),
            "username": username,
            "text": text,
        }
        if icon_url is not None:
            args["icon_url"] = icon_url
        if attachments is not None:
            args["attachments"] = attachments
        try_sending(
            self._log, self.connect, "Slack", self.__client.chat_postMessage, args
        )

    # Returns a string s that is in proper channel format
    @staticmethod
    def channel_format(name):
        if name[0] == "#":  # Remove # if added
            name = name[1:]
        name = name.replace("\u2642", "m").replace("\u2640", "f").lower()
        return re.sub("[^_a-z0-9-]+", "", name)

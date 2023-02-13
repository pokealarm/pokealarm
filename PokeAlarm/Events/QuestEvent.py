# Standard Library Imports
from datetime import datetime

# 3rd Party Imports
# Local Imports
from PokeAlarm import Unknown
from . import BaseEvent
from PokeAlarm.Utils import (
    get_gmaps_link,
    get_applemaps_link,
    get_waze_link,
    get_dist_as_str,
    get_base_types,
    get_type_emoji,
    get_shiny_emoji,
)
from PokeAlarm.Utilities.QuestUtils import reward_string, get_item_id, get_quest_image
from PokeAlarm.Utilities.MonUtils import get_shiny_status


class QuestEvent(BaseEvent):
    """Event representing the discovery of a Quest."""

    def __init__(self, data):
        """Creates a new Quest Event based on the given dict."""
        super(QuestEvent, self).__init__("quests")
        check_for_none = BaseEvent.check_for_none

        # Identification
        self.stop_id = data["pokestop_id"]
        self.stop_name = check_for_none(
            str, data.get("pokestop_name", data.get("name")), Unknown.REGULAR
        )
        self.stop_image = check_for_none(
            str, data.get("pokestop_url", data.get("url")), Unknown.REGULAR
        )

        # Location
        self.lat = float(data["latitude"])
        self.lng = float(data["longitude"])

        # Completed by Manager
        self.distance = Unknown.SMALL
        self.direction = Unknown.TINY

        # Used to reject
        self.name = self.stop_id
        self.geofence = Unknown.REGULAR
        self.custom_dts = {}

        # Quest Details
        self.quest_type_raw = data["quest_type"]
        self.quest_type_id = data.get("quest_type_raw")
        self.quest_target = data.get("quest_target")
        self.quest_task_raw = data.get("quest_task")
        self.quest_condition_raw = data.get("quest_condition")
        self.quest_template = data.get("quest_template")
        self.last_modified = datetime.utcfromtimestamp(data["timestamp"])

        # Reward Details
        self.reward_type_id = data["quest_reward_type_raw"]
        self.reward_type_raw = data.get("quest_reward_type")
        self.reward_amount = data.get("item_amount", 1)

        # Monster Reward Details
        self.monster_id = data.get("pokemon_id", 0)
        self.monster_form_id = data.get("pokemon_form", 0)
        self.monster_costume_id = data.get("pokemon_costume", 0)
        self.monster_types = (
            get_base_types(self.monster_id, self.monster_form_id)
            if self.monster_id != 0
            else [0, 0]
        )
        self.monster_can_be_shiny = (
            get_shiny_status(self.monster_id, self.monster_form_id)
            if self.monster_id != 0
            else False
        )

        # Item Reward Details
        self.item_amount = self.reward_amount
        self.item_type = data.get("item_type")
        self.item_id = data.get("item_id", 0)

    def update_with_cache(self, cache):
        """Update event infos using cached data from previous events."""

        # Nothing to update
        pass

    def generate_dts(self, locale, timezone, units):
        """Return a dict with all the DTS for this event."""
        form_name = locale.get_form_name(self.monster_id, self.monster_form_id)
        costume_name = locale.get_costume_name(self.monster_id, self.monster_costume_id)
        type1 = locale.get_type_name(self.monster_types[0])
        type2 = locale.get_type_name(self.monster_types[1])
        dts = self.custom_dts.copy()
        dts.update(
            {
                # Identification
                "stop_id": self.stop_id,
                "stop_name": self.stop_name,
                "stop_image": self.stop_image,
                # Location
                "lat": self.lat,
                "lng": self.lng,
                "lat_5": f"{self.lat:.5f}",
                "lng_5": f"{self.lng:.5f}",
                "distance": (
                    get_dist_as_str(self.distance, units)
                    if Unknown.is_not(self.distance)
                    else Unknown.SMALL
                ),
                "direction": self.direction,
                "gmaps": get_gmaps_link(self.lat, self.lng, False),
                "gnav": get_gmaps_link(self.lat, self.lng, True),
                "applemaps": get_applemaps_link(self.lat, self.lng, False),
                "applenav": get_applemaps_link(self.lat, self.lng, True),
                "waze": get_waze_link(self.lat, self.lng, False),
                "wazenav": get_waze_link(self.lat, self.lng, True),
                "geofence": self.geofence,
                # Quest Details
                # ToDo: Interpret the 'quest_condition' field and use that instead
                #  of 'quest_type'
                #  Will be able to better serve manager specific locales
                #  also do this for 'quest_task'
                "quest_type": self.quest_type_raw,
                "quest_type_id": self.quest_type_id,
                "quest_target": self.quest_target,
                "quest_task": self.quest_task_raw,
                "quest_template": self.quest_template,
                "last_modified": self.last_modified,
                "quest_condition": self.quest_condition_raw,
                "quest_image": get_quest_image(self),
                # Reward Details
                "reward_type_id": self.reward_type_id,
                "reward_type": locale.get_quest_type_name(self.reward_type_id),
                "reward_type_raw": self.reward_type_raw,
                "reward_amount": self.item_amount,
                "reward": reward_string(self, locale),
                # Monster Reward Details
                "mon_name": locale.get_pokemon_name(self.monster_id),
                "mon_id": self.monster_id,
                "mon_id_3": f"{self.monster_id:03}",
                "form": form_name,
                "form_or_empty": Unknown.or_empty(form_name),
                "nonnormal_form_or_empty": (
                    ""
                    if locale.get_english_form_name(
                        self.monster_id, self.monster_form_id
                    )
                    == "Normal"
                    else Unknown.or_empty(form_name)
                ),
                "form_id": self.monster_form_id,
                "form_id_2": f"{self.monster_form_id:02d}",
                "form_id_3": f"{self.monster_form_id:03d}",
                "costume": costume_name,
                "costume_or_empty": Unknown.or_empty(costume_name),
                "costume_id": self.monster_costume_id,
                "costume_id_2": f"{self.monster_costume_id:02d}",
                "costume_id_3": f"{self.monster_costume_id:03d}",
                "type1": type1,
                "type1_or_empty": Unknown.or_empty(type1),
                "type1_emoji": Unknown.or_empty(get_type_emoji(self.monster_types[0])),
                "type2": type2,
                "type2_or_empty": Unknown.or_empty(type2),
                "type2_emoji": Unknown.or_empty(get_type_emoji(self.monster_types[1])),
                "types": (f"{type1}/{type2}" if Unknown.is_not(type2) else type1),
                "types_emoji": (
                    f"{get_type_emoji(self.monster_types[0])}{get_type_emoji(self.monster_types[1])}"
                    if Unknown.is_not(type2)
                    else get_type_emoji(self.monster_types[0])
                ),
                "shiny_emoji": get_shiny_emoji(self.monster_can_be_shiny),
                # Item Reward Details
                "raw_item_type": self.item_type,
                "item": get_item_id(self.item_id),
                "item_id": self.item_id,
                "item_id_4": f"{self.item_id:04d}",
                "current_timestamp_utc": datetime.utcnow(),
            }
        )
        return dts

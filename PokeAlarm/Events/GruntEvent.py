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
    get_time_as_str,
    get_seconds_remaining,
    get_dist_as_str,
    get_type_emoji,
    get_gender_sym,
    is_weather_boosted,
    get_cached_weather_id_from_coord,
    get_weather_emoji,
)
from PokeAlarm.Utilities.GruntUtils import (
    get_grunt_gender_id,
    get_grunt_mon_type_id,
    get_grunt_reward_mon_id,
    get_grunt_mon_battle,
    get_grunt_name,
)


class GruntEvent(BaseEvent):
    """Event representing the invasion of a PokeStop."""

    def __init__(self, data):
        """Creates a new Stop Event based on the given dict."""
        super(GruntEvent, self).__init__("grunt")
        check_for_none = BaseEvent.check_for_none

        # Identification
        self.stop_id = data["pokestop_id"]

        # Details
        self.stop_name = check_for_none(
            str, data.get("pokestop_name") or data.get("name"), Unknown.REGULAR
        )
        self.stop_image = check_for_none(
            str, data.get("pokestop_url") or data.get("url"), Unknown.REGULAR
        )

        # Time
        self.start = datetime.utcfromtimestamp(
            data.get("incident_start", data.get("start", 0))
        )
        self.expiration = datetime.utcfromtimestamp(
            data.get("incident_expiration", data.get("expiration", 0))
        )
        self.time_left = None
        if self.expiration is not None:
            self.time_left = get_seconds_remaining(self.expiration)

        # Grunt type ID
        self.grunt_type_id = check_for_none(
            int, data.get("incident_grunt_type", data.get("character")), 0
        )
        self.grunt_name = get_grunt_name(self.grunt_type_id)

        # Cosmetic
        self.display_type = check_for_none(str, data.get("display_type"), 0)
        self.style = check_for_none(str, data.get("style"), 0)

        # Grunt gender
        self.gender_id = get_grunt_gender_id(self.grunt_type_id)
        self.gender = get_gender_sym(self.gender_id)

        # Mon type
        self.mon_type_id = get_grunt_mon_type_id(self.grunt_type_id)

        # Possible mon reward
        self.reward_mon_ids = get_grunt_reward_mon_id(self.grunt_type_id)

        # Possible mon battle
        self.mon_battle1_ids = get_grunt_mon_battle(self.grunt_type_id, 1)
        self.mon_battle2_ids = get_grunt_mon_battle(self.grunt_type_id, 2)
        self.mon_battle3_ids = get_grunt_mon_battle(self.grunt_type_id, 3)

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

        # Weather (updated later with cache)
        self.weather_id = None
        self.boosted_weather_id = None

    def update_with_cache(self, cache):
        """Update event infos using cached data from previous events."""

        # Update weather
        weather_id = get_cached_weather_id_from_coord(self.lat, self.lng, cache)
        if Unknown.is_not(weather_id):
            self.weather_id = BaseEvent.check_for_none(int, weather_id, Unknown.TINY)
            self.boosted_weather_id = (
                0 if Unknown.is_not(self.weather_id) else Unknown.TINY
            )
            if is_weather_boosted(
                weather_id=self.weather_id, mon_type=self.mon_type_id
            ):
                self.boosted_weather_id = self.weather_id

    def generate_dts(self, locale, timezone, units):
        """Return a dict with all the DTS for this event."""
        start_time = get_time_as_str(self.start, timezone)
        expiration_time = get_time_as_str(self.expiration, timezone)
        dts = self.custom_dts.copy()
        weather_name = locale.get_weather_name(self.weather_id)
        boosted_weather_name = locale.get_weather_name(self.boosted_weather_id)
        dts.update(
            {
                # Identification
                "stop_id": self.stop_id,
                # Details
                "stop_name": self.stop_name,
                "stop_image": self.stop_image,
                "grunt_id": self.grunt_type_id,
                "grunt_id_3": f"{self.grunt_type_id:03}",
                "grunt_name": self.grunt_name,
                "type_name": locale.get_type_name(self.mon_type_id),
                "type_emoji": get_type_emoji(self.mon_type_id),
                "gender_id": self.gender_id,
                "gender": self.gender,
                "display_type": self.display_type,
                "style": self.style,
                # Rewards
                "reward_ids": ", ".join(map(str, self.reward_mon_ids)),
                "reward_names": ", ".join(
                    map(str, [locale.get_pokemon_name(x) for x in self.reward_mon_ids])
                ),
                # Battle
                "battle1_ids": ", ".join(map(str, self.mon_battle1_ids)),
                "battle2_ids": ", ".join(map(str, self.mon_battle2_ids)),
                "battle3_ids": ", ".join(map(str, self.mon_battle3_ids)),
                "battle1_names": ", ".join(
                    map(str, [locale.get_pokemon_name(x) for x in self.mon_battle1_ids])
                ),
                "battle2_names": ", ".join(
                    map(str, [locale.get_pokemon_name(x) for x in self.mon_battle2_ids])
                ),
                "battle3_names": ", ".join(
                    map(str, [locale.get_pokemon_name(x) for x in self.mon_battle3_ids])
                ),
                # Start Time
                "start_time": start_time[0],
                "12h_start_time": start_time[1],
                "24h_start_time": start_time[2],
                "start_time_no_secs": start_time[3],
                "12h_start_time_no_secs": start_time[4],
                "24h_start_time_no_secs": start_time[5],
                "start_time_raw_hours": start_time[6],
                "start_time_raw_minutes": start_time[7],
                "start_time_raw_seconds": start_time[8],
                "start_utc": self.start,
                # Time left
                "time_left": expiration_time[0],
                "12h_time": expiration_time[1],
                "24h_time": expiration_time[2],
                "time_left_no_secs": expiration_time[3],
                "12h_time_no_secs": expiration_time[4],
                "24h_time_no_secs": expiration_time[5],
                "time_left_raw_hours": expiration_time[6],
                "time_left_raw_minutes": expiration_time[7],
                "time_left_raw_seconds": expiration_time[8],
                "expiration_utc": self.expiration,
                "current_timestamp_utc": datetime.utcnow(),
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
                # Weather
                "weather_id": self.weather_id,
                "weather": weather_name,
                "weather_or_empty": Unknown.or_empty(weather_name),
                "weather_emoji": get_weather_emoji(self.weather_id),
                "boosted_weather_id": self.boosted_weather_id,
                "boosted_weather": boosted_weather_name,
                "boosted_weather_or_empty": (
                    ""
                    if self.boosted_weather_id == 0
                    else Unknown.or_empty(boosted_weather_name)
                ),
                "boosted_weather_emoji": get_weather_emoji(self.boosted_weather_id),
                "boosted_or_empty": locale.get_boosted_text()
                if Unknown.is_not(self.boosted_weather_id)
                and self.boosted_weather_id != 0
                else "",
            }
        )
        return dts

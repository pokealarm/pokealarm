# Standard Library Imports
from datetime import datetime

# 3rd Party Imports
# Local Imports
from PokeAlarm.Utils import (
    get_time_as_str,
    get_seconds_remaining,
    get_gmaps_link,
    get_applemaps_link,
    get_waze_link,
    get_dist_as_str,
    get_weather_emoji,
    get_team_emoji,
    get_ex_eligible_emoji,
)
from . import BaseEvent
from PokeAlarm import Unknown


class EggEvent(BaseEvent):
    """Event representing the change occurred in a Gym."""

    def __init__(self, data):
        """Creates a new Stop Event based on the given dict."""
        super(EggEvent, self).__init__("egg")
        check_for_none = BaseEvent.check_for_none

        # Identification
        self.gym_id = data.get("gym_id")

        # Time Remaining
        self.egg_spawn_utc = datetime.utcfromtimestamp(data.get("spawn", 0))
        self.raid_start_utc = datetime.utcfromtimestamp(data.get("start", 0))
        self.raid_end_utc = datetime.utcfromtimestamp(data.get("end", 0))
        self.time_left = get_seconds_remaining(self.raid_start_utc)

        # Location
        self.lat = float(data["latitude"])
        self.lng = float(data["longitude"])
        self.distance = Unknown.SMALL  # Completed by Manager
        self.direction = Unknown.TINY  # Completed by Manager
        self.weather_id = check_for_none(int, data.get("weather"), Unknown.TINY)

        # Egg Info
        self.egg_lvl = check_for_none(int, data.get("level"), 0)

        # Gym Details
        self.gym_name = check_for_none(
            str, data.get("name", data.get("gym_name")), Unknown.REGULAR
        ).strip()
        self.gym_description = check_for_none(
            str, data.get("description"), Unknown.REGULAR
        ).strip()
        self.gym_image = check_for_none(
            str, data.get("url", data.get("gym_url")), Unknown.REGULAR
        )
        self.slots_available = Unknown.TINY
        self.guard_count = Unknown.TINY

        self.sponsor_id = check_for_none(int, data.get("sponsor"), Unknown.TINY)
        self.partner_id = check_for_none(
            int, data.get("partner_id"), Unknown.TINY
        )  # RDM only
        self.park = check_for_none(str, data.get("park"), Unknown.REGULAR)
        self.ex_eligible = check_for_none(
            int,
            data.get("is_ex_raid_eligible", data.get("ex_raid_eligible")),
            Unknown.REGULAR,
        )
        self.is_exclusive = check_for_none(
            int, data.get("is_exclusive"), Unknown.REGULAR
        )

        # Gym Team (this is only available from cache)
        self.current_team_id = check_for_none(
            int, data.get("team_id", data.get("team")), Unknown.TINY
        )

        self.name = self.gym_id
        self.geofence = Unknown.REGULAR
        self.custom_dts = {}

    def update_with_cache(self, cache):
        """Update event infos using cached data from previous events."""

        # Update available slots
        self.slots_available = cache.gym_slots(self.gym_id)
        self.guard_count = (
            (6 - self.slots_available)
            if Unknown.is_not(self.slots_available)
            else Unknown.TINY
        )

    def generate_dts(self, locale, timezone, units):
        """Return a dict with all the DTS for this event."""
        egg_spawn = get_time_as_str(self.egg_spawn_utc, timezone)
        raid_start = get_time_as_str(self.raid_start_utc, timezone)
        raid_end = get_time_as_str(self.raid_end_utc, timezone)
        weather_name = locale.get_weather_name(self.weather_id)
        dts = self.custom_dts.copy()
        dts.update(
            {
                # Identification
                "gym_id": self.gym_id,
                # Spawn Time
                "spawn_time": egg_spawn[0],
                "12h_spawn_time": egg_spawn[1],
                "24h_spawn_time": egg_spawn[2],
                "spawn_time_no_secs": egg_spawn[3],
                "12h_spawn_time_no_secs": egg_spawn[4],
                "24h_spawn_time_no_secs": egg_spawn[5],
                "spawn_time_raw_hours": egg_spawn[6],
                "spawn_time_raw_minutes": egg_spawn[7],
                "spawn_time_raw_seconds": egg_spawn[8],
                "spawn_time_utc": self.egg_spawn_utc.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                # Hatch Time Remaining
                "hatch_time_left": raid_start[0],
                "12h_hatch_time": raid_start[1],
                "24h_hatch_time": raid_start[2],
                "hatch_time_no_secs": raid_start[3],
                "12h_hatch_time_no_secs": raid_start[4],
                "24h_hatch_time_no_secs": raid_start[5],
                "hatch_time_raw_hours": raid_start[6],
                "hatch_time_raw_minutes": raid_start[7],
                "hatch_time_raw_seconds": raid_start[8],
                "hatch_time_utc": self.raid_start_utc.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                # Raid Time Remaining
                "raid_time_left": raid_end[0],
                "12h_raid_end": raid_end[1],
                "24h_raid_end": raid_end[2],
                "raid_time_no_secs": raid_end[3],
                "12h_raid_end_no_secs": raid_end[4],
                "24h_raid_end_no_secs": raid_end[5],
                "raid_time_raw_hours": raid_end[6],
                "raid_time_raw_minutes": raid_end[7],
                "raid_time_raw_seconds": raid_end[8],
                "raid_end_utc": self.raid_end_utc.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
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
                "weather_id": self.weather_id,
                "weather": weather_name,
                "weather_or_empty": Unknown.or_empty(weather_name),
                "weather_emoji": get_weather_emoji(self.weather_id),
                # Egg info
                "egg_lvl": self.egg_lvl,
                # Gym Details
                "gym_name": self.gym_name,
                "gym_description": self.gym_description,
                "gym_image": self.gym_image,
                "slots_available": self.slots_available,
                "guard_count": self.guard_count,
                "sponsor_id": self.sponsor_id,
                "sponsored": self.sponsor_id > 0
                if Unknown.is_not(self.sponsor_id)
                else Unknown.REGULAR,
                "partner_id": self.partner_id,
                "ex_eligible": self.ex_eligible > 0
                if Unknown.is_not(self.ex_eligible)
                else Unknown.REGULAR,
                "ex_eligible_emoji": get_ex_eligible_emoji(self.ex_eligible),
                "is_exclusive": self.is_exclusive > 0
                if Unknown.is_not(self.is_exclusive)
                else Unknown.REGULAR,
                "park": self.park,
                "team_id": self.current_team_id,
                "team_emoji": get_team_emoji(self.current_team_id),
                "team_name": locale.get_team_name(self.current_team_id),
                "team_color": locale.get_team_color(self.current_team_id),
                "team_leader": locale.get_leader_name(self.current_team_id),
            }
        )
        return dts

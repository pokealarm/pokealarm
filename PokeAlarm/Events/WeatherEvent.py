# Standard Library Imports
from datetime import datetime

# 3rd Party Imports
# Local Imports
from PokeAlarm.Utils import (
    get_gmaps_link,
    get_applemaps_link,
    get_dist_as_str,
    get_weather_emoji,
    get_waze_link,
)
from . import BaseEvent
from PokeAlarm import Unknown


class WeatherEvent(BaseEvent):
    """Event representing the change occurred in Weather."""

    def __init__(self, data):
        """Creates a new Weather Event based on the given dict."""
        super(WeatherEvent, self).__init__("weather")
        check_for_none = BaseEvent.check_for_none

        # Identification
        self.s2_cell_id = check_for_none(int, data.get("s2_cell_id"), Unknown.SMALL)
        self.s2_cell_coords = check_for_none(str, data.get("coords"), Unknown.SMALL)

        # Location
        self.lat = float(data["latitude"])  # To the center of the cell
        self.lng = float(data["longitude"])
        self.distance = Unknown.SMALL  # Completed by Manager
        self.direction = Unknown.TINY  # Completed by Manager

        # Weather Info
        self.weather_id = check_for_none(
            int, data.get("condition") or data.get("gameplay_condition"), 0
        )
        self.severity_id = check_for_none(
            int, data.get("alert_severity") or data.get("severity"), 0
        )
        self.day_or_night_id = data.get("day") or data.get("world_time")
        self.wind_direction = check_for_none(
            int, data.get("wind_direction"), Unknown.TINY
        )
        self.warn_weather = check_for_none(int, data.get("warn_weather"), Unknown.TINY)

        # Weather levels
        self.cloud_level = check_for_none(int, data.get("cloud_level"), Unknown.TINY)
        self.rain_level = check_for_none(int, data.get("rain_level"), Unknown.TINY)
        self.wind_level = check_for_none(int, data.get("wind_level"), Unknown.TINY)
        self.snow_level = check_for_none(int, data.get("snow_level"), Unknown.TINY)
        self.fog_level = check_for_none(int, data.get("fog_level"), Unknown.TINY)
        self.special_effect_level = check_for_none(
            int, data.get("special_effect_level"), Unknown.TINY
        )

        self.updated = check_for_none(bool, data.get("updated"), Unknown.TINY)

        self.name = self.s2_cell_id
        self.geofence = Unknown.REGULAR
        self.custom_dts = {}

    def update_with_cache(self, cache):
        """Update event infos using cached data from previous events."""

        # Nothing to update
        pass

    def generate_dts(self, locale, timezone, units):
        """Return a dict with all the DTS for this event."""
        weather_name = locale.get_weather_name(self.weather_id)
        severity_locale = locale.get_severity_name(self.severity_id)
        dts = self.custom_dts.copy()
        dts.update(
            {
                # Identification
                "s2_cell_id": self.s2_cell_id,
                "s2_cell_coords": self.s2_cell_coords,
                # Location - center of the s2 cell
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
                # Weather Info
                "weather_id": self.weather_id,
                "weather_id_3": f"{self.weather_id:03}",
                "weather": weather_name,
                "weather_emoji": get_weather_emoji(self.weather_id),
                "severity_id": self.severity_id,
                "severity_id_3": f"{self.severity_id:03}",
                "severity": severity_locale,
                "severity_or_empty": "" if self.severity_id == 0 else severity_locale,
                "day_or_night_id": self.day_or_night_id,
                "day_or_night_id_3": f"{self.day_or_night_id:03}",
                "day_or_night": locale.get_day_or_night(self.day_or_night_id),
                "wind_direction": self.wind_direction,
                "warn_weather": self.warn_weather,
                # Weather Levels
                "cloud_level": self.cloud_level,
                "rain_level": self.rain_level,
                "wind_level": self.wind_level,
                "snow_level": self.snow_level,
                "fog_level": self.fog_level,
                "special_effect_level": self.special_effect_level,
                "updated": self.updated,
                "current_timestamp_utc": datetime.utcnow(),
            }
        )
        return dts

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
)


class StopEvent(BaseEvent):
    """Event representing the discovery of a PokeStop."""

    def __init__(self, data):
        """Creates a new Stop Event based on the given dict."""
        super(StopEvent, self).__init__("stop")
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
        self.lure_type_id = check_for_none(int, data.get("lure_id"), 0)

        # Time left
        self.expiration = datetime.utcfromtimestamp(data.get("lure_expiration"))

        self.time_left = None
        if self.expiration is not None:
            self.time_left = get_seconds_remaining(self.expiration)

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

    def update_with_cache(self, cache):
        """Update event infos using cached data from previous events."""

        # Nothing to update
        pass

    def generate_dts(self, locale, timezone, units):
        """Return a dict with all the DTS for this event."""
        time = get_time_as_str(self.expiration, timezone)
        dts = self.custom_dts.copy()
        dts.update(
            {
                # Identification
                "stop_id": self.stop_id,
                # Details
                "stop_name": self.stop_name,
                "stop_image": self.stop_image,
                "lure_type_id": self.lure_type_id,
                "lure_type_id_3": "{:03}".format(self.lure_type_id),
                "lure_type_name": locale.get_lure_type_name(self.lure_type_id),
                # Time left
                "time_left": time[0],
                "12h_time": time[1],
                "24h_time": time[2],
                "time_left_no_secs": time[3],
                "12h_time_no_secs": time[4],
                "24h_time_no_secs": time[5],
                "time_left_raw_hours": time[6],
                "time_left_raw_minutes": time[7],
                "time_left_raw_seconds": time[8],
                "expiration_utc": self.expiration,
                "current_timestamp_utc": datetime.utcnow(),
                # Location
                "lat": self.lat,
                "lng": self.lng,
                "lat_5": "{:.5f}".format(self.lat),
                "lng_5": "{:.5f}".format(self.lng),
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
            }
        )
        return dts

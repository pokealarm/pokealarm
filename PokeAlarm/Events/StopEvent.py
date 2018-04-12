# Standard Library Imports
from datetime import datetime
# 3rd Party Imports
# Local Imports
from PokeAlarm import Unknown
from . import BaseEvent
from PokeAlarm.Utils import get_gmaps_link, get_applemaps_link, \
    get_waze_link, get_time_as_str, get_seconds_remaining, get_dist_as_str


class StopEvent(BaseEvent):
    """ Event representing the discovery of a PokeStop. """

    def __init__(self, data):
        """ Creates a new Stop Event based on the given dict. """
        super(StopEvent, self).__init__('stop')

        # Identification
        self.stop_id = data['pokestop_id']

        # Time left
        self.expiration = data['lure_expiration']
        self.time_left = None
        if self.expiration is not None:
            self.expiration = datetime.utcfromtimestamp(self.expiration)
            self.time_left = get_seconds_remaining(self.expiration)

        # Location
        self.lat = float(data['latitude'])
        self.lng = float(data['longitude'])

        # Completed by Manager
        self.distance = Unknown.SMALL
        self.direction = Unknown.TINY

        # Used to reject
        self.name = self.stop_id
        self.geofence = Unknown.REGULAR
        self.custom_dts = {}

    def generate_dts(self, locale, timezone, units):
        """ Return a dict with all the DTS for this event. """
        time = get_time_as_str(self.expiration, timezone)
        dts = self.custom_dts.copy()
        dts.update({
            # Identification
            'stop_id': self.stop_id,

            # Time left
            'time_left': time[0],
            '12h_time': time[1],
            '24h_time': time[2],

            # Location
            'lat': self.lat,
            'lng': self.lng,
            'lat_5': "{:.5f}".format(self.lat),
            'lng_5': "{:.5f}".format(self.lat),
            'distance': (
                get_dist_as_str(self.distance, units)
                if Unknown.is_not(self.distance) else Unknown.SMALL),
            'direction': self.direction,
            'gmaps': get_gmaps_link(self.lat, self.lng),
            'applemaps': get_applemaps_link(self.lat, self.lng),
            'waze': get_waze_link(self.lat, self.lng),
            'geofence': self.geofence
        })
        return dts

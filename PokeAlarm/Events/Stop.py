# Standard Library Imports
from datetime import datetime
# 3rd Party Imports
# Local Imports
from PokeAlarm import Unknown
from . import Event
from PokeAlarm.Utils import get_gmaps_link, get_applemaps_link, \
    get_time_as_str, get_dist_as_str


class Stop(Event):
    """ Event representing the discovery of a PokeStop. """

    def __init__(self, data):
        """ Creates a new Stop Event based on the given dict. """
        super(Stop, self).__init__('stop')

        # Identification
        self.id = data['pokestop_id']

        # Time left
        self.expiration = datetime.utcfromtimestamp(data['lure_expiration'])

        # Location
        self.lat = float(data['latitude'])
        self.lng = float(data['longitude'])
        self.distance = Unknown.SMALL  # Completed by Manager
        self.direction = Unknown.TINY  # Completed by Manager

    def generate_dts(self, locale):
        """ Return a dict with all the DTS for this event. """
        time = get_time_as_str(self.expiration)
        return {
            # Identification
            'id': self.id,

            # Time left
            'time_left': time[0],
            '12h_time': time[1],
            '24h_time': time[2],

            # Location
            'lat': self.lat,
            'lng': self.lng,
            'lat_5': "{:.5f}".format(self.lat),
            'lng_5': "{:.5f}".format(self.lat),
            'distance': get_dist_as_str(self.distance),
            'direction': self.direction,
            'gmaps': get_gmaps_link(self.lat, self.lng),
            'applemaps': get_applemaps_link(self.lat, self.lng),
        }

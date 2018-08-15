# Standard Library Imports
import datetime
# 3rd Party Imports
# Local Imports
from PokeAlarm import Unknown
from . import BaseEvent
from PokeAlarm.Utils import get_gmaps_link, get_applemaps_link, \
    get_dist_as_str


class QuestEvent(BaseEvent):
    """ Event representing the discovery of a PokeStop. """

    def __init__(self, data):
        """ Creates a new Quest Event based on the given dict. """
        super(QuestEvent, self).__init__('quest')

        # Identification
        self.stop_id = data['pokestop_id']
        self.stop_name = data['name']
        self.stop_image = data['url']

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

        # Quest Details
        self.quest = data['quest']
        self.reward = data['reward']
        self.expiry = datetime.datetime.now().strftime("%d/%m/%Y 23:59")

    def generate_dts(self, locale, timezone, units):
        """ Return a dict with all the DTS for this event. """
        dts = self.custom_dts.copy()
        dts.update({
            # Identification
            'stop_id': self.stop_id,
            'stop_name': self.stop_name,
            'stop_image': self.stop_image,
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
            'geofence': self.geofence,
            # Quest Details
            'quest': self.quest,
            'reward': self.reward,
            'expiry': self.expiry
        })
        return dts

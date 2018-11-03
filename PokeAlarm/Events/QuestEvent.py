# Standard Library Imports
import datetime
# 3rd Party Imports
# Local Imports
from PokeAlarm import Unknown
from . import BaseEvent
from PokeAlarm.Utils import get_gmaps_link, get_applemaps_link, \
    get_waze_link, get_dist_as_str


class QuestEvent(BaseEvent):
    """ Event representing the discovery of a Quest. """

    def __init__(self, data):
        """ Creates a new Quest Event based on the given dict. """
        super(QuestEvent, self).__init__('quests')
        check_for_none = BaseEvent.check_for_none

        # Identification
        self.stop_id = data['pokestop_id']
        self.stop_name = check_for_none(
            str, data.get('pokestop_name') or data.get('name'),
            Unknown.REGULAR)
        self.stop_image = check_for_none(
            str, data.get('pokestop_url') or data.get('url'), Unknown.REGULAR)

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
        self.expire_time = datetime.datetime.now().strftime("%d/%m/%Y 23:59")
        self.reward_type = check_for_none(int, data.get('type'), 0)

    def generate_dts(self, locale, timezone, units):
        """ Return a dict with all the DTS for this event. """
        type_name = locale.get_quest_type_name(self.reward_type)

        dts = self.custom_dts.copy()
        dts.update({
            # Identification
            'stop_id': self.stop_id,
            'stop_name': self.stop_name,
            'stop_image': self.stop_image,
            'reward_type_id': self.reward_type,
            'reward_type': type_name,
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
            'geofence': self.geofence,
            # Quest Details
            'quest': self.quest,
            'reward': self.reward,
            'expire_time': self.expire_time,
            'time_remaining': self.expire_time
        })
        return dts

# Standard Library Imports
# 3rd Party Imports
# Local Imports
from PokeAlarm.Utils import get_gmaps_link, get_applemaps_link, \
    get_waze_link, get_dist_as_str
from . import BaseEvent
from PokeAlarm import Unknown


class GymEvent(BaseEvent):
    """ Event representing the change occurred in a Gym. """

    def __init__(self, data):
        """ Creates a new Gym Event based on the given dict. """
        super(GymEvent, self).__init__('gym')
        check_for_none = BaseEvent.check_for_none

        # Identification
        self.gym_id = data.get('gym_id', data.get('id'))

        # Location
        self.lat = float(data['latitude'])
        self.lng = float(data['longitude'])
        self.distance = Unknown.SMALL  # Completed by Manager
        self.direction = Unknown.TINY  # Completed by Manager

        # Team Info
        self.old_team_id = Unknown.TINY
        self.new_team_id = int(data.get('team_id', data.get('team')))

        # Gym Details
        self.gym_name = check_for_none(
            str, data.get('name'), Unknown.REGULAR).strip()
        self.gym_description = check_for_none(
            str, data.get('description'), Unknown.REGULAR).strip()
        self.gym_image = check_for_none(
            str, data.get('url'), Unknown.REGULAR)

        # Gym Guards
        self.slots_available = check_for_none(
            int, data.get('slots_available'), Unknown.TINY)
        self.guard_count = (
            (6 - self.slots_available)
            if Unknown.is_not(self.slots_available)
            else Unknown.TINY)

        self.name = self.gym_id
        self.geofence = Unknown.REGULAR
        self.custom_dts = {}

    def generate_dts(self, locale, timezone, units):
        """ Return a dict with all the DTS for this event. """
        dts = self.custom_dts.copy()
        dts.update({
            # Identification
            'gym_id': self.gym_id,

            # Location
            'lat': self.lat,
            'lng': self.lng,
            'lat_5': "{:.5f}".format(self.lat),
            'lng_5': "{:.5f}".format(self.lng),
            'distance': (
                get_dist_as_str(self.distance, units)
                if Unknown.is_not(self.distance) else Unknown.SMALL),
            'direction': self.direction,
            'gmaps': get_gmaps_link(self.lat, self.lng),
            'applemaps': get_applemaps_link(self.lat, self.lng),
            'waze': get_waze_link(self.lat, self.lng),
            'geofence': self.geofence,

            # Team Info
            'old_team': locale.get_team_name(self.old_team_id),
            'old_team_id': self.old_team_id,
            'old_team_leader': locale.get_leader_name(self.old_team_id),
            'new_team': locale.get_team_name(self.new_team_id),
            'new_team_id': self.new_team_id,
            'new_team_leader': locale.get_leader_name(self.new_team_id),

            # Details
            'gym_name': self.gym_name,
            'gym_description': self.gym_description,
            'gym_image': self.gym_image,

            # Guards
            'slots_available': self.slots_available,
            'guard_count': self.guard_count,
        })
        return dts

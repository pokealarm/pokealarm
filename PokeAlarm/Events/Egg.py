# Standard Library Imports
from datetime import datetime
# 3rd Party Imports
# Local Imports
from PokeAlarm.Utils import get_time_as_str, get_gmaps_link, \
    get_applemaps_link, get_dist_as_str
from . import Event
from PokeAlarm import Unknown


class Egg(Event):
    """ Event representing the change occurred in a Gym. """

    def __init__(self, data):
        """ Creates a new Stop Event based on the given dict. """
        super(Egg, self).__init__('egg')
        check_for_none = Event.check_for_none

        # Identification
        self.gym_id = data.get('gym_id')

        # Time Remaining
        self.hatch_time = datetime.utcfromtimestamp(
            data.get('start') or data.get('raid_begin'))  # RM or Monocle
        self.raid_end = datetime.utcfromtimestamp(
            data.get('end') or data.get('raid_end'))  # RM or Monocle

        # Location
        self.lat = float(data['latitude'])
        self.lng = float(data['longitude'])
        self.distance = Unknown.SMALL  # Completed by Manager
        self.direction = Unknown.TINY  # Completed by Manager

        # Egg Info
        self.egg_level = check_for_none(int, data.get('level'), 0)

        # Gym Details (currently only sent from Monocle)
        self.gym_name = check_for_none(
            str, data.get('name'), Unknown.REGULAR).strip()
        self.gym_description = check_for_none(
            str, data.get('description'), Unknown.REGULAR).strip()
        self.gym_image_url = check_for_none(
            str, data.get('url'), Unknown.REGULAR)
        self.current_team_id = Unknown.TINY

    def generate_dts(self, locale):
        """ Return a dict with all the DTS for this event. """
        hatch_time = get_time_as_str(self.hatch_time)
        raid_end_time = get_time_as_str(self.raid_end)
        return {
            # Identification
            'gym_id': self.gym_id,

            # Time Remaining
            'hatch_time_left': hatch_time[0],
            '12h_hatch_time': hatch_time[1],
            '24h_hatch_time': hatch_time[2],
            'raid_end': raid_end_time[0],
            '12h_raid_end': raid_end_time[1],
            '24h_raid_end': raid_end_time[2],

            # Location
            'lat': self.lat,
            'lng': self.lng,
            'lat_5': "{:.5f}".format(self.lat),
            'lng_5': "{:.5f}".format(self.lng),
            'distance': get_dist_as_str(self.distance),
            'direction': self.direction,
            'gmaps': get_gmaps_link(self.lat, self.lng),
            'applemaps': get_applemaps_link(self.lat, self.lng),

            # Egg info
            'egg_level': self.egg_level,

            # Gym Details
            'gym_name': self.gym_name,
            'gym_description': self.gym_description,
            'gym_image_url': self.gym_image_url,
            'team_id': self.current_team_id,
            'team_name': locale.get_team_name(self.current_team_id),
            'team_leader': locale.get_leader_name(self.current_team_id)
        }

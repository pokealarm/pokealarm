# Standard Library Imports
from datetime import datetime
# 3rd Party Imports
# Local Imports
from PokeAlarm.Utils import get_time_as_str, get_seconds_remaining, \
    get_gmaps_link, get_applemaps_link, get_waze_link, get_dist_as_str, \
    get_weather_emoji
from . import BaseEvent
from PokeAlarm import Unknown


class EggEvent(BaseEvent):
    """ Event representing the change occurred in a Gym. """

    def __init__(self, data):
        """ Creates a new Stop Event based on the given dict. """
        super(EggEvent, self).__init__('egg')
        check_for_none = BaseEvent.check_for_none

        # Identification
        self.gym_id = data.get('gym_id')

        # Time Remaining
        self.hatch_time = datetime.utcfromtimestamp(
            data.get('start') or data.get('raid_begin'))  # RM or Monocle
        self.time_left = get_seconds_remaining(self.hatch_time)
        self.raid_end = datetime.utcfromtimestamp(
            data.get('end') or data.get('raid_end'))  # RM or Monocle

        # Location
        self.lat = float(data['latitude'])
        self.lng = float(data['longitude'])
        self.distance = Unknown.SMALL  # Completed by Manager
        self.direction = Unknown.TINY  # Completed by Manager
        self.weather_id = check_for_none(
            int, data.get('weather'), Unknown.TINY)

        # Egg Info
        self.egg_lvl = check_for_none(int, data.get('level'), 0)

        # Gym Details (currently only sent from Monocle)
        self.gym_name = check_for_none(
            str, data.get('name'), Unknown.REGULAR).strip()
        self.gym_description = check_for_none(
            str, data.get('description'), Unknown.REGULAR).strip()
        self.gym_image = check_for_none(
            str, data.get('url'), Unknown.REGULAR)
        self.sponsor_id = check_for_none(
            int, data.get('sponsor'), Unknown.TINY)
        self.park = check_for_none(
            str, data.get('park'), Unknown.REGULAR)

        # Gym Team (this is only available from cache)
        self.current_team_id = check_for_none(
            int, data.get('team_id', data.get('team')), Unknown.TINY)

        self.name = self.gym_id
        self.geofence = Unknown.REGULAR
        self.custom_dts = {}

    def generate_dts(self, locale, timezone, units):
        """ Return a dict with all the DTS for this event. """
        hatch_time = get_time_as_str(self.hatch_time, timezone)
        raid_end_time = get_time_as_str(self.raid_end, timezone)
        weather_name = locale.get_weather_name(self.weather_id)
        dts = self.custom_dts.copy()
        dts.update({
            # Identification
            'gym_id': self.gym_id,

            # Time Remaining
            'hatch_time_left': hatch_time[0],
            '12h_hatch_time': hatch_time[1],
            '24h_hatch_time': hatch_time[2],
            'raid_time_left': raid_end_time[0],
            '12h_raid_end': raid_end_time[1],
            '24h_raid_end': raid_end_time[2],

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
            'weather_id': self.weather_id,
            'weather': weather_name,
            'weather_or_empty': Unknown.or_empty(weather_name),
            'weather_emoji': get_weather_emoji(self.weather_id),

            # Egg info
            'egg_lvl': self.egg_lvl,

            # Gym Details
            'gym_name': self.gym_name,
            'gym_description': self.gym_description,
            'gym_image': self.gym_image,
            'sponsor_id': self.sponsor_id,
            'sponsored':
                self.sponsor_id > 0
                if Unknown.is_not(self.sponsor_id) else Unknown.REGULAR,
            'park': self.park,
            'team_id': self.current_team_id,
            'team_name': locale.get_team_name(self.current_team_id),
            'team_leader': locale.get_leader_name(self.current_team_id)
        })
        return dts

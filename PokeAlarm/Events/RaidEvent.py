# Standard Library Imports
from datetime import datetime
# 3rd Party Imports
# Local Imports
from PokeAlarm import Unknown
from . import BaseEvent
from PokeAlarm.Utils import get_gmaps_link, get_applemaps_link, \
    get_time_as_str, get_move_damage, get_move_dps, get_move_duration, \
<<<<<<< HEAD
    get_move_energy, get_dist_as_str, get_pokemon_cp_range
=======
    get_move_energy, get_dist_as_str
>>>>>>> f93f49fde6df6f2f9398d44e52a545a3dc6f2921


class RaidEvent(BaseEvent):
    """ Event representing the discovery of a Raid. """

    def __init__(self, data):
        """ Creates a new Stop Event based on the given dict. """
        super(RaidEvent, self).__init__('raid')
        check_for_none = BaseEvent.check_for_none

        # Identification
        self.gym_id = data.get('gym_id')

        # Time Remaining
        self.raid_end = datetime.utcfromtimestamp(
            data.get('end') or data.get('raid_end'))  # RM or Monocle

        # Location
        self.lat = float(data['latitude'])
        self.lng = float(data['longitude'])
        self.distance = Unknown.SMALL  # Completed by Manager
        self.direction = Unknown.TINY  # Completed by Manager

        # Monster Info
        self.raid_lvl = int(data['level'])
        self.mon_id = int(data['pokemon_id'])
<<<<<<< HEAD
        self.cp = int(data['cp'])
=======
>>>>>>> f93f49fde6df6f2f9398d44e52a545a3dc6f2921
        # Quick Move
        self.quick_id = check_for_none(int, data.get('move_1'), Unknown.TINY)
        self.quick_damage = get_move_damage(self.quick_id)
        self.quick_dps = get_move_dps(self.quick_id)
        self.quick_duration = get_move_duration(self.quick_id)
        self.quick_energy = get_move_energy(self.quick_id)
        # Charge Move
        self.charge_id = check_for_none(int, data.get('move_2'), Unknown.TINY)
        self.charge_damage = get_move_damage(self.charge_id)
        self.charge_dps = get_move_dps(self.charge_id)
        self.charge_duration = get_move_duration(self.quick_id)
        self.charge_energy = get_move_energy(self.charge_id)

        # Gym Details (currently only sent from Monocle)
        self.gym_name = check_for_none(
            str, data.get('name'), Unknown.REGULAR).strip()
        self.gym_description = check_for_none(
            str, data.get('description'), Unknown.REGULAR).strip()
        self.gym_image = check_for_none(
            str, data.get('url'), Unknown.REGULAR)

        # Gym Team (this is only available from cache)
        self.current_team_id = check_for_none(
            int, data.get('team'), Unknown.TINY)

        self.name = self.gym_id
        self.geofence = Unknown.REGULAR
        self.custom_dts = {}

    def generate_dts(self, locale):
        """ Return a dict with all the DTS for this event. """
        raid_end_time = get_time_as_str(self.raid_end)
        dts = self.custom_dts.copy()
<<<<<<< HEAD
        cp_range = get_pokemon_cp_range(self.mon_id, 20)
=======
>>>>>>> f93f49fde6df6f2f9398d44e52a545a3dc6f2921
        dts.update({
            # Identification
            'gym_id': self.gym_id,

            # Time Remaining
            'raid_time_left': raid_end_time[0],
            '12h_raid_end': raid_end_time[1],
            '24h_raid_end': raid_end_time[2],

            # Location
            'lat': self.lat,
            'lng': self.lng,
            'lat_5': "{:.5f}".format(self.lat),
            'lng_5': "{:.5f}".format(self.lng),
            'distance': (
                get_dist_as_str(self.distance) if Unknown.is_not(self.distance)
                else Unknown.SMALL),
            'direction': self.direction,
            'gmaps': get_gmaps_link(self.lat, self.lng),
            'applemaps': get_applemaps_link(self.lat, self.lng),
            'geofence': self.geofence,

            # Raid Info
            'raid_lvl': self.raid_lvl,
            'mon_name': locale.get_pokemon_name(self.mon_id),
            'mon_id': self.mon_id,
            'mon_id_3': "{:03}".format(self.mon_id),
            # TODO: Form?

            # Quick Move
            'quick_move': locale.get_move_name(self.quick_id),
            'quick_id': self.quick_id,
            'quick_damage': self.quick_damage,
            'quick_dps': self.quick_dps,
            'quick_duration': self.quick_duration,
            'quick_energy': self.quick_energy,
            # Charge Move
            'charge_move': locale.get_move_name(self.charge_id),
            'charge_id': self.charge_id,
            'charge_damage': self.charge_damage,
            'charge_dps': self.charge_dps,
            'charge_duration': self.charge_duration,
            'charge_energy': self.charge_energy,
<<<<<<< HEAD
            # CP info
            'cp': self.cp,
            'min_cp': cp_range[0],
            'max_cp': cp_range[1],
=======
>>>>>>> f93f49fde6df6f2f9398d44e52a545a3dc6f2921

            # Gym Details
            'gym_name': self.gym_name,
            'gym_description': self.gym_description,
            'gym_image': self.gym_image,
            'team_id': self.current_team_id,
            'team_name': locale.get_team_name(self.current_team_id),
            'team_leader': locale.get_leader_name(self.current_team_id)
        })
        return dts

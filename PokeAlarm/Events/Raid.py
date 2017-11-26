# Standard Library Imports
from datetime import datetime
# 3rd Party Imports
# Local Imports
from PokeAlarm import Unknown
from . import Event
from PokeAlarm.Utils import get_gmaps_link, get_applemaps_link, \
    get_time_as_str, get_move_damage, get_move_dps, get_move_duration, \
    get_move_energy, get_dist_as_str


class Raid(Event):
    """ Event representing the discovery of a Raid. """

    def __init__(self, data):
        """ Creates a new Stop Event based on the given dict. """
        super(Raid, self).__init__('raid')
        check_for_none = Event.check_for_none

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
        self.raid_level = check_for_none(int, data.get('level'), Unknown.TINY)
        self.pkmn_id = check_for_none(
            int, data.get('pokemon_id'), Unknown.TINY)
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
        self.gym_image_url = check_for_none(
            str, data.get('url'), Unknown.REGULAR)
        self.current_team_id = Unknown.TINY  # Will set later

    def generate_dts(self, locale):
        """ Return a dict with all the DTS for this event. """
        raid_end_time = get_time_as_str(self.raid_end)
        return {
            # Identification
            'gym_id': self.gym_id,

            # Time Remaining
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

            # Raid Info
            'raid_level': self.raid_level,
            'pkmn': locale.get_pokemon_name(self.pkmn_id),
            'pkmn_id': self.pkmn_id,
            'pkmn_id_3': "{:03}".format(self.pkmn_id),
            # TODO: Form?

            # Quick Move
            'quick_move': locale.get_move_name(self.quick_id),
            'quick_id': self.quick_id,
            'quick_damage': self.quick_damage,
            'quick_dps': self.quick_dps,
            'quick_duration': self.quick_duration,
            'quick_energy': self.quick_energy,
            # Charge Move
            'charge_id': locale.get_move_name(self.quick_id),
            'charge_damage': self.charge_damage,
            'charge_dps': self.charge_dps,
            'charge_duration': self.charge_duration,
            'charge_energy': self.charge_energy,

            # Gym Details
            'gym_name': self.gym_name,
            'gym_description': self.gym_description,
            'gym_image_url': self.gym_image_url,
            'team_id': self.current_team_id,
            'team_name': locale.get_team_name(self.current_team_id),
            'team_leader': locale.get_leader_name(self.current_team_id)
        }

# Standard Library Imports
from datetime import datetime
# 3rd Party Imports
# Local Imports
from PokeAlarm import Unknown
from PokeAlarm.Utils import get_gmaps_link, get_move_damage, get_move_dps, \
    get_move_duration, get_move_energy, get_pokemon_gender, get_pokemon_size, \
    get_applemaps_link, get_time_as_str, get_dist_as_str
from . import Event


class Monster(Event):
    """ Event representing the discovery of a Pokemon. """

    def __init__(self, data):
        """ Creates a new Monster Event based on the given dict. """
        super(Monster, self).__init__('monster')
        check_for_none = Event.check_for_none

        # Identification
        self.enc_id = data['encounter_id']
        self.pkmn_id = int(data['pokemon_id'])

        # Time Left
        self.despawn_time = datetime.utcfromtimestamp(data['disappear_time'])
        self.seconds_remaining = int(data.get('seconds_until_despawn'))

        # Spawn Data
        self.spawn_start = check_for_none(
            int, data.get('spawn_start'), Unknown.REGULAR)
        self.spawn_end = check_for_none(
            int, data.get('spawn_end'), Unknown.REGULAR)
        self.spawn_verified = check_for_none(bool, data.get('verified'), False)

        # Location
        self.lat = float(data['latitude'])
        self.lng = float(data['longitude'])
        self.distance = Unknown.SMALL  # Completed by Manager
        self.direction = Unknown.TINY  # Completed by Manager

        # Encounter Stats
        self.pkmn_lvl = check_for_none(int, data.get('cp'), Unknown.TINY)
        self.cp = check_for_none(int, data.get('cp'), Unknown.TINY)
        # IVs
        self.atk = check_for_none(
            int, data.get('individual_attack'), Unknown.TINY)
        self.dfe = check_for_none(
            int, data.get('individual_defense'), Unknown.TINY)
        self.sta = check_for_none(
            int, data.get('individual_stamina'), Unknown.TINY)
        if Unknown.is_not(self.atk, self.dfe, self.sta):
            self.iv = 100 * (self.atk + self.dfe + self.sta) / float(45)
        else:
            self.iv - Unknown.SMALL
        # Form
        self.form_id = check_for_none(int, data.get('form'), Unknown.TINY)
        if self.form_id == 0:  # TODO: Change this before pulling 3.5
            self.form_id = Unknown.TINY

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

        # Cosmetic
        self.gender = get_pokemon_gender(
            check_for_none(int, data.get('gender'), Unknown.TINY)),
        self.height = check_for_none(float, data.get('height'), Unknown.SMALL)
        self.weight = check_for_none(float, data.get('weight'), Unknown.SMALL)
        self.size = get_pokemon_size(self.pkmn_id, self.height, self.weight)

    def generate_dts(self, locale):
        """ Return a dict with all the DTS for this event. """
        time = get_time_as_str(self.despawn_time)
        form_name = locale.get_form_name(self.form_id)
        return {
            # Identification
            'enc_id': self.enc_id,
            'pkmn': locale.get_pokemon_name(self.pkmn_id),
            'pkmn_id': self.pkmn_id,
            'pkmn_id_3': "{:03}".format(self.pkmn_id),

            # Time Remaining
            'time_left': time[0],
            '12h_time': time[1],
            '24h_time': time[2],
            'seconds_remaining': self.seconds_remaining,

            # Spawn Data
            'spawn_start': self.spawn_start,
            'spawn_end': self.spawn_end,
            'spawn_verified': self.spawn_verified,

            # Location
            'lat': self.lat,
            'lng': self.lng,
            'lat_5': "{:.5f}".format(self.lat),
            'lng_5': "{:.5f}".format(self.lng),
            'distance': get_dist_as_str(self.distance),
            'direction': self.direction,
            'gmaps': get_gmaps_link(self.lat, self.lng),
            'applemaps': get_applemaps_link(self.lat, self.lng),

            # Encounter Stats
            'pkmn_lvl': self.pkmn_lvl,
            'cp': self.cp,
            # IVs
            'iv_0': (
                ":.0f".format(self.iv) if Unknown.is_not(self.iv)
                else Unknown.TINY),
            'iv': (
                ":.1f".format(self.iv) if Unknown.is_not(self.iv)
                else Unknown.SMALL),
            'iv_2': (
                ":.2f".format(self.iv) if Unknown.is_not(self.iv)
                else Unknown.SMALL),
            'atk': self.atk,
            'def': self.dfe,
            'sta': self.sta,
            # Form
            'form': form_name,
            'form_or_empty': Unknown.or_empty(form_name),
            'form_id': self.form_id,
            'form_id_3_or_empty': (
                ":.3f".format(self.iv) if Unknown.is_not(self.form_id)
                else Unknown.TINY),

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

            # Cosmetic
            'gender': self.gender,
            'height': self.height,
            'weight': self.weight,
            'size': self.size
        }

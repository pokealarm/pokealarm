# Standard Library Imports
from datetime import datetime
# 3rd Party Imports
# Local Imports
from PokeAlarm import Unknown
from PokeAlarm.Utilities import MonUtils
from PokeAlarm.Utils import (
    get_gmaps_link, get_move_damage, get_move_dps, get_move_duration,
    get_move_energy, get_pokemon_size, get_applemaps_link, get_time_as_str,
    get_dist_as_str, get_weather_emoji)
from . import BaseEvent


class MonEvent(BaseEvent):
    """ Event representing the discovery of a Pokemon. """

    def __init__(self, data):
        """ Creates a new Monster Event based on the given dict. """
        super(MonEvent, self).__init__('monster')
        check_for_none = BaseEvent.check_for_none

        # Identification
        self.enc_id = data['encounter_id']
        self.monster_id = int(data['pokemon_id'])

        # Time Left
        self.disappear_time = datetime.utcfromtimestamp(data['disappear_time'])

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
        self.weather_id = check_for_none(
            int, data.get('weather'), Unknown.TINY)

        # Encounter Stats
        self.mon_lvl = check_for_none(
            int, data.get('pokemon_level'), Unknown.TINY)
        self.cp = check_for_none(int, data.get('cp'), Unknown.TINY)
        # IVs
        self.atk_iv = check_for_none(
            int, data.get('individual_attack'), Unknown.TINY)
        self.def_iv = check_for_none(
            int, data.get('individual_defense'), Unknown.TINY)
        self.sta_iv = check_for_none(
            int, data.get('individual_stamina'), Unknown.TINY)
        if Unknown.is_not(self.atk_iv, self.def_iv, self.sta_iv):
            self.iv = \
                100 * (self.atk_iv + self.def_iv + self.sta_iv) / float(45)
        else:
            self.iv = Unknown.SMALL
        # Form
        self.form_id = check_for_none(int, data.get('form'), 0)

        # Quick Move
        self.quick_move_id = check_for_none(
            int, data.get('move_1'), Unknown.TINY)
        self.quick_damage = get_move_damage(self.quick_move_id)
        self.quick_dps = get_move_dps(self.quick_move_id)
        self.quick_duration = get_move_duration(self.quick_move_id)
        self.quick_energy = get_move_energy(self.quick_move_id)
        # Charge Move
        self.charge_move_id = check_for_none(
            int, data.get('move_2'), Unknown.TINY)
        self.charge_damage = get_move_damage(self.charge_move_id)
        self.charge_dps = get_move_dps(self.charge_move_id)
        self.charge_duration = get_move_duration(self.quick_move_id)
        self.charge_energy = get_move_energy(self.charge_move_id)

        # Cosmetic
        self.gender = MonUtils.get_gender_sym(
            check_for_none(int, data.get('gender'), Unknown.TINY))

        self.height = check_for_none(float, data.get('height'), Unknown.SMALL)
        self.weight = check_for_none(float, data.get('weight'), Unknown.SMALL)
        if Unknown.is_not(self.height, self.weight):
            self.size = get_pokemon_size(
                self.monster_id, self.height, self.weight)
        else:
            self.size = Unknown.SMALL

        # Correct this later
        self.name = self.monster_id
        self.geofence = Unknown.REGULAR
        self.custom_dts = {}

    def generate_dts(self, locale, timezone, units):
        """ Return a dict with all the DTS for this event. """
        time = get_time_as_str(self.disappear_time, timezone)
        form_name = locale.get_form_name(self.monster_id, self.form_id)
        weather_name = locale.get_weather_name(self.weather_id)
        dts = self.custom_dts.copy()
        dts.update({
            # Identification
            'encounter_id': self.enc_id,
            'mon_name': locale.get_pokemon_name(self.monster_id),
            'mon_id': self.monster_id,
            'mon_id_3': "{:03}".format(self.monster_id),

            # Time Remaining
            'time_left': time[0],
            '12h_time': time[1],
            '24h_time': time[2],

            # Spawn Data
            'spawn_start': self.spawn_start,
            'spawn_end': self.spawn_end,
            'spawn_verified': self.spawn_verified,

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
            'geofence': self.geofence,
            'weather_id': self.weather_id,
            'weather': weather_name,
            'weather_or_empty': Unknown.or_empty(weather_name),
            'weather_emoji': get_weather_emoji(self.weather_id),

            # Encounter Stats
<<<<<<< HEAD
            'mon_lvl': self.mon_lvl,
=======
            'pkmn_lvl': self.mon_lvl,
>>>>>>> f93f49fde6df6f2f9398d44e52a545a3dc6f2921
            'cp': self.cp,
            # IVs
            'iv_0': (
                "{:.0f}".format(self.iv) if Unknown.is_not(self.iv)
                else Unknown.TINY),
            'iv': (
                "{:.1f}".format(self.iv) if Unknown.is_not(self.iv)
                else Unknown.SMALL),
            'iv_2': (
                "{:.2f}".format(self.iv) if Unknown.is_not(self.iv)
                else Unknown.SMALL),
            'atk': self.atk_iv,
            'def': self.def_iv,
            'sta': self.sta_iv,
            # Form
            'form': form_name,
            'form_or_empty': Unknown.or_empty(form_name),
            'form_id': self.form_id,
            'form_id_3': "{:03d}".format(self.form_id),

            # Quick Move
            'quick_move': locale.get_move_name(self.quick_move_id),
            'quick_id': self.quick_move_id,
            'quick_damage': self.quick_damage,
            'quick_dps': self.quick_dps,
            'quick_duration': self.quick_duration,
            'quick_energy': self.quick_energy,
            # Charge Move
            'charge_move': locale.get_move_name(self.charge_move_id),
            'charge_id': self.charge_move_id,
            'charge_damage': self.charge_damage,
            'charge_dps': self.charge_dps,
            'charge_duration': self.charge_duration,
            'charge_energy': self.charge_energy,

            # Cosmetic
            'gender': self.gender,
            'height': self.height,
            'weight': self.weight,
<<<<<<< HEAD
            'size': self.size,

            # Misc
            'big_karp': (
                'big' if self.monster_id == 129 and Unknown.is_not(self.weight)
                and self.weight >= 13.13 else ''),
            'tiny_rat': (
                'tiny' if self.monster_id == 19 and Unknown.is_not(self.weight)
                and self.weight <= 2.41 else '')
=======
            'size': self.size
>>>>>>> f93f49fde6df6f2f9398d44e52a545a3dc6f2921
        })
        return dts

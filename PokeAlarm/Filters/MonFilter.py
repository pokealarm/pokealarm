# Standard Library Imports
import operator
# 3rd Party Imports
# Local Imports
from . import BaseFilter
from PokeAlarm.Utilities import MonUtils as MonUtils
from PokeAlarm.Utils import get_weather_id


class MonFilter(BaseFilter):
    """ Filter class for limiting which monsters trigger a notification. """

    def __init__(self, mgr, name, data):
        """ Initializes base parameters for a filter. """
        super(MonFilter, self).__init__(mgr, 'monster', name)

        # Monster ID - f.monster_ids contains m.monster_id
        self.monster_ids = self.evaluate_attribute(  #
            event_attribute='monster_id', eval_func=operator.contains,
            limit=BaseFilter.parse_as_set(
                MonUtils.get_monster_id, 'monsters', data))

        # Exclude Monsters - f.monster_ids not contains m.ex_mon_id
        self.exclude_monster_ids = self.evaluate_attribute(  #
            event_attribute='monster_id',
            eval_func=lambda d, v: not operator.contains(d, v),
            limit=BaseFilter.parse_as_set(
                MonUtils.get_monster_id, 'monsters_exclude', data))

        # Distance
        self.min_dist = self.evaluate_attribute(  # f.min_dist <= m.distance
            event_attribute='distance', eval_func=operator.le,
            limit=BaseFilter.parse_as_type(float, 'min_dist', data))
        self.max_dist = self.evaluate_attribute(  # f.max_dist <= m.distance
            event_attribute='distance', eval_func=operator.ge,
            limit=BaseFilter.parse_as_type(float, 'max_dist', data))

        # Time Left
        self.min_time_left = self.evaluate_attribute(
            # f.min_time_left <= r.time_left
            event_attribute='time_left', eval_func=operator.le,
            limit=BaseFilter.parse_as_type(int, 'min_time_left', data))
        self.max_time_left = self.evaluate_attribute(
            # f.max_time_left >= r.time_left
            event_attribute='time_left', eval_func=operator.ge,
            limit=BaseFilter.parse_as_type(int, 'max_time_left', data))

        # Encounter Stats
        # Level
        self.min_lvl = self.evaluate_attribute(  # f.min_lvl <= m.mon_lvl
            event_attribute='mon_lvl', eval_func=operator.le,
            limit=BaseFilter.parse_as_type(int, 'min_lvl', data))
        self.max_lvl = self.evaluate_attribute(  # f.max_lvl >= m.mon_lvl
            event_attribute='mon_lvl', eval_func=operator.ge,
            limit=BaseFilter.parse_as_type(int, 'max_lvl', data))
        # CP
        self.min_cp = self.evaluate_attribute(  # f.min_cp <= m.cp
            event_attribute='cp', eval_func=operator.le,
            limit=BaseFilter.parse_as_type(int, 'min_cp', data))
        self.max_cp = self.evaluate_attribute(  # f.max_cp >= m.cp
            event_attribute='cp', eval_func=operator.ge,
            limit=BaseFilter.parse_as_type(int, 'max_cp', data))
        # Attack IV
        self.min_atk = self.evaluate_attribute(  # f.min_atk <= m.atk_iv
            event_attribute='atk_iv', eval_func=operator.le,
            limit=BaseFilter.parse_as_type(int, 'min_atk', data))
        self.max_atk = self.evaluate_attribute(  # f.max_atk >= m.atk_iv
            event_attribute='atk_iv', eval_func=operator.ge,
            limit=BaseFilter.parse_as_type(int, 'max_atk', data))
        # Defense IV
        self.min_def = self.evaluate_attribute(  # f.min_def <= m.def_iv
            event_attribute='def_iv', eval_func=operator.le,
            limit=BaseFilter.parse_as_type(int, 'min_def', data))
        self.max_def = self.evaluate_attribute(  # f.max_def >= m.def_iv
            event_attribute='def_iv', eval_func=operator.ge,
            limit=BaseFilter.parse_as_type(int, 'max_def', data))
        # Stamina IV
        self.min_sta = self.evaluate_attribute(  # f.min_sta <= m.sta_iv
            event_attribute='sta_iv', eval_func=operator.le,
            limit=BaseFilter.parse_as_type(int, 'min_sta', data))
        self.max_sta = self.evaluate_attribute(  # f.max_sta >= m.sta_iv
            event_attribute='sta_iv', eval_func=operator.ge,
            limit=BaseFilter.parse_as_type(int, 'max_sta', data))
        # Percent IV
        self.min_iv = self.evaluate_attribute(  # f.min_iv <= m.iv
            event_attribute='iv', eval_func=operator.le,
            limit=BaseFilter.parse_as_type(float, 'min_iv', data))
        self.max_iv = self.evaluate_attribute(  # f.max_iv >= m.iv
            event_attribute='iv', eval_func=operator.ge,
            limit=BaseFilter.parse_as_type(float, 'max_iv', data))
        # Form  TODO: names
        self.forms = self.evaluate_attribute(  # f.forms in m.form_id
            event_attribute='form_id', eval_func=operator.contains,
            limit=BaseFilter.parse_as_set(int, 'form_ids', data))
        # Costume  TODO: names
        self.costumes = self.evaluate_attribute(  # f.costumes in m.costume_id
            event_attribute='costume_id', eval_func=operator.contains,
            limit=BaseFilter.parse_as_set(int, 'costume_ids', data))

        # Quick Move
        self.quick_moves = self.evaluate_attribute(  # f.q_ms contains m.q_m
            event_attribute='quick_id', eval_func=operator.contains,
            limit=BaseFilter.parse_as_set(
                MonUtils.get_move_id, 'quick_moves', data))

        # Charge Move
        self.charge_moves = self.evaluate_attribute(  # f.c_ms contains m.c_m
            event_attribute='charge_id', eval_func=operator.contains,
            limit=BaseFilter.parse_as_set(
                MonUtils.get_move_id, 'charge_moves', data))

        # Cosmetic
        # Gender
        self.genders = self.evaluate_attribute(  # f.genders contains m.gender
            event_attribute='gender', eval_func=operator.contains,
            limit=BaseFilter.parse_as_set(
                MonUtils.get_gender_sym, 'genders', data))
        # Height
        self.min_height = self.evaluate_attribute(  # f.min_height <= m.height
            event_attribute='height', eval_func=operator.le,
            limit=BaseFilter.parse_as_type(float, 'min_height', data))
        self.max_height = self.evaluate_attribute(  # f.max_height >= m.height
            event_attribute='height', eval_func=operator.ge,
            limit=BaseFilter.parse_as_type(float, 'max_height', data))
        # Weight
        self.min_weight = self.evaluate_attribute(  # f.min_weight <= m.weight
            event_attribute='weight', eval_func=operator.le,
            limit=BaseFilter.parse_as_type(float, 'min_weight', data))
        self.max_weight = self.evaluate_attribute(  # f.max_weight >= m.weight
            event_attribute='weight', eval_func=operator.ge,
            limit=BaseFilter.parse_as_type(float, 'max_weight', data))
        # Size
        self.sizes = self.evaluate_attribute(  # f.sizes in m.size_id
            event_attribute='size_id', eval_func=operator.contains,
            limit=BaseFilter.parse_as_set(
                MonUtils.get_size_id, 'sizes', data))

        # Weather
        self.weather_ids = self.evaluate_attribute(
            event_attribute='weather_id', eval_func=operator.contains,
            limit=BaseFilter.parse_as_set(get_weather_id, 'weather', data))

        # Rarity
        self.rarity_ids = self.evaluate_attribute(  #
            event_attribute='rarity_id', eval_func=operator.contains,
            limit=BaseFilter.parse_as_set(
                MonUtils.get_rarity_id, 'rarity', data))

        # Geofences
        self.geofences = BaseFilter.parse_as_list(str, 'geofences', data)

        # Custom DTS
        self.custom_dts = BaseFilter.parse_as_dict(
            str, str, 'custom_dts', data)

        # Missing Info
        self.is_missing_info = BaseFilter.parse_as_type(
            bool, 'is_missing_info', data)

        # Reject leftover parameters
        for key in data:
            raise ValueError("'{}' is not a recognized parameter for"
                             " Monster filters".format(key))

    def to_dict(self):
        """ Create a dict representation of this Filter. """
        settings = {}
        # Monster ID
        if self.monster_ids is not None:
            settings['monster_ids'] = self.monster_ids

        # Distance
        if self.min_dist is not None:
            settings['min_dist'] = self.min_dist
        if self.max_dist is not None:
            settings['max_dist'] = self.max_dist

        # Level
        if self.min_lvl is not None:
            settings['min_lvl'] = self.min_lvl
        if self.max_lvl is not None:
            settings['max_lvl'] = self.max_lvl
        # Attack IV
        if self.min_atk is not None:
            settings['min_atk'] = self.min_atk
        if self.max_atk is not None:
            settings['max_atk'] = self.max_atk
        # Defense IV
        if self.min_def is not None:
            settings['min_def'] = self.min_def
        if self.max_def is not None:
            settings['max_def'] = self.max_def
        # Stamina IV
        if self.min_atk is not None:
            settings['min_atk'] = self.min_atk
        if self.min_sta is not None:
            settings['min_sta'] = self.min_sta
        # Percent IV
        if self.min_iv is not None:
            settings['min_iv'] = self.min_iv
        if self.max_iv is not None:
            settings['max_iv'] = self.max_iv
        # Form
        if self.forms is not None:
            settings['forms'] = self.forms
        # Costume
        if self.forms is not None:
            settings['costumes'] = self.costumes

        # Quick Move
        if self.quick_moves is not None:
            settings['quick_moves'] = self.quick_moves
        # Charge Move
        if self.charge_moves is not None:
            settings['charge_moves'] = self.charge_moves

        # Cosmetic
        if self.genders is not None:
            settings['genders'] = self.genders
        # Height
        if self.min_height is not None:
            settings['min_height'] = self.min_height
        if self.max_height is not None:
            settings['max_height'] = self.max_height
        # Weight
        if self.min_weight is not None:
            settings['min_weight'] = self.min_weight
        if self.max_weight is not None:
            settings['max_weight'] = self.max_weight
        # Size
        if self.sizes is not None:
            settings['sizes'] = self.sizes

        # Weather
        if self.weather_ids is not None:
            settings['weather_ids'] = self.weather_ids

        # Geofences
        if self.geofences is not None:
            settings['geofences'] = self.geofences

        # Missing Info
        if self.is_missing_info is not None:
            settings['missing_info'] = self.is_missing_info

        return settings

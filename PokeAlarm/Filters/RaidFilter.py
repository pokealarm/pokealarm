# Standard Library Imports
import operator
import re
# 3rd Party Imports
# Local Imports
from . import Filter
from PokeAlarm.Utilities import MonUtils as MonUtils
from PokeAlarm.Utilities import GymUtils as GymUtils


class Raid(Filter):
    """ Filter class for limiting which egg trigger a notification. """

    def __init__(self, name, data):
        """ Initializes base parameters for a filter. """
        super(Raid, self).__init__(name)

        # Monster ID - f.monster_ids in r.monster_id
        self.monster_ids = self.evaluate_attribute(  #
            event_attribute='monster_id', eval_func=operator.contains,
            limit=Filter.parse_as_set(
                MonUtils.get_monster_id, 'monsters', data))

        # Distance
        self.min_dist = self.evaluate_attribute(  # f.min_dist <= r.distance
            event_attribute='distance', eval_func=operator.le,
            limit=Filter.parse_as_type(int, 'min_dist', data))
        self.max_dist = self.evaluate_attribute(  # f.max_dist <= r.distance
            event_attribute='distance', eval_func=operator.ge,
            limit=Filter.parse_as_type(int, 'max_dist', data))

        # Monster Info
        self.min_lvl = self.evaluate_attribute(  # f.min_lvl <= r.mon_lvl
            event_attribute='mon_lvl', eval_func=operator.le,
            limit=Filter.parse_as_type(int, 'min_lvl', data))
        self.max_lvl = self.evaluate_attribute(  # f.max_lvl >= r.mon_lvl
            event_attribute='mon_lvl', eval_func=operator.ge,
            limit=Filter.parse_as_type(int, 'max_lvl', data))
        # Attack IV
        self.min_atk = self.evaluate_attribute(  # f.min_atk <= r.atk_iv
            event_attribute='atk_iv', eval_func=operator.le,
            limit=Filter.parse_as_type(int, 'min_atk', data))
        self.max_atk = self.evaluate_attribute(  # f.max_atk >= r.atk_iv
            event_attribute='atk_iv', eval_func=operator.ge,
            limit=Filter.parse_as_type(int, 'max_atk', data))
        # Defense IV
        self.min_def = self.evaluate_attribute(  # f.min_def <= r.def_iv
            event_attribute='def_iv', eval_func=operator.le,
            limit=Filter.parse_as_type(int, 'min_def', data))
        self.max_def = self.evaluate_attribute(  # f.max_def >= r.def_iv
            event_attribute='def_iv', eval_func=operator.ge,
            limit=Filter.parse_as_type(int, 'max_def', data))
        # Stamina IV
        self.min_sta = self.evaluate_attribute(  # f.min_sta <= r.sta_iv
            event_attribute='sta_iv', eval_func=operator.le,
            limit=Filter.parse_as_type(int, 'min_sta', data))
        self.max_sta = self.evaluate_attribute(  # f.max_sta >= r.sta_iv
            event_attribute='sta_iv', eval_func=operator.ge,
            limit=Filter.parse_as_type(int, 'max_sta', data))
        # Percent IV
        self.min_iv = self.evaluate_attribute(  # f.min_iv <= r.iv
            event_attribute='iv', eval_func=operator.le,
            limit=Filter.parse_as_type(float, 'min_iv', data))
        self.max_iv = self.evaluate_attribute(  # f.max_iv >= r.iv
            event_attribute='iv', eval_func=operator.ge,
            limit=Filter.parse_as_type(float, 'max_iv', data))

        # Quick Move
        self.quick_moves = self.evaluate_attribute(  # f.q_ms contains r.q_m
            event_attribute='quick_move_id', eval_func=operator.contains,
            limit=Filter.parse_as_set(
                MonUtils.get_move_id, 'quick_moves', data))
        # Charge Move
        self.charge_moves = self.evaluate_attribute(  # f.c_ms contains r.c_m
            event_attribute='charge_move_id', eval_func=operator.contains,
            limit=Filter.parse_as_set(
                MonUtils.get_move_id, 'charge_moves', data))

        # Gym name
        self.gym_name_matches = self.evaluate_attribute(  # f.gn matches e.gn
            event_attribute='gym_name', eval_func=GymUtils.match_regex_dict,
            limit=Filter.parse_as_set(re.compile, 'gym_name_matches', data))

        # Missing Info
        self.missing_info = Filter.parse_as_type(bool, 'missing_info', data)

        # Reject leftover parameters
        for key in data:
            raise ValueError("'{}' is not a recognized parameter for"
                             " Egg filters".format(key))

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

        # Gym Name
        if self.gym_name_matches is not None:
            settings['gym_name_matches'] = self.gym_name_matches

        # Missing Info
        if self.missing_info is not None:
            settings['missing_info'] = self.missing_info

        return settings

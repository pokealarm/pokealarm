# Standard Library Imports
import operator
# 3rd Party Imports
# Local Imports
from . import BaseFilter
from PokeAlarm.Utilities import GymUtils as GymUtils


class EggFilter(BaseFilter):
    """ Filter class for limiting which egg trigger a notification. """

    def __init__(self, mgr, name, data):
        """ Initializes base parameters for a filter. """
        super(EggFilter, self).__init__(mgr, 'egg', name)

        # Distance
        self.min_dist = self.evaluate_attribute(  # f.min_dist <= e.distance
            event_attribute='distance', eval_func=operator.le,
            limit=BaseFilter.parse_as_type(float, 'min_dist', data))
        self.max_dist = self.evaluate_attribute(  # f.max_dist <= e.distance
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

        # Egg Level
        # Level
        self.min_lvl = self.evaluate_attribute(  # f.min_lvl <= e.egg_lvl
            event_attribute='egg_lvl', eval_func=operator.le,
            limit=BaseFilter.parse_as_type(int, 'min_egg_lvl', data))
        self.max_lvl = self.evaluate_attribute(  # f.max_lvl >= e.egg_lvl
            event_attribute='egg_lvl', eval_func=operator.ge,
            limit=BaseFilter.parse_as_type(int, 'max_egg_lvl', data))

        # Gym name
        self.gym_name_contains = self.evaluate_attribute(  # f.gn matches e.gn
            event_attribute='gym_name', eval_func=GymUtils.match_regex_dict,
            limit=BaseFilter.parse_as_set(
                GymUtils.create_regex, 'gym_name_contains', data))
        self.gym_name_excludes = self.evaluate_attribute(  # f.gn no-match e.gn
            event_attribute='gym_name',
            eval_func=GymUtils.not_match_regex_dict,
            limit=BaseFilter.parse_as_set(
                GymUtils.create_regex, 'gym_name_excludes', data))

        # Gym sponsor
        self.sponsored = self.evaluate_attribute(
            event_attribute='sponsor_id', eval_func=lambda y, x: (x > 0) == y,
            limit=BaseFilter.parse_as_type(bool, 'sponsored', data))

        # Gym park
        self.park_contains = self.evaluate_attribute(  # f.gp matches e.gp
            event_attribute='park', eval_func=GymUtils.match_regex_dict,
            limit=BaseFilter.parse_as_set(
                GymUtils.create_regex, 'park_contains', data))

        # Team Info
        self.old_team = self.evaluate_attribute(  # f.ctis contains m.cti
            event_attribute='current_team_id', eval_func=operator.contains,
            limit=BaseFilter.parse_as_set(
                GymUtils.get_team_id, 'current_teams', data))

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
                             " Egg filters".format(key))

    def to_dict(self):
        """ Create a dict representation of this Filter. """
        settings = {}

        # Distance
        if self.min_dist is not None:
            settings['min_dist'] = self.min_dist
        if self.max_dist is not None:
            settings['max_dist'] = self.max_dist

        # Levels
        if self.min_lvl is not None:
            settings['min_lvl'] = self.min_lvl
        if self.max_lvl is not None:
            settings['max_lvl'] = self.max_lvl

        # Gym Name
        if self.gym_name_contains is not None:
            settings['gym_name_contains'] = self.gym_name_contains

        if self.gym_name_excludes is not None:
            settings['gym_name_excludes'] = self.gym_name_excludes

        # Gym Sponsor
        if self.sponsored is not None:
            settings['sponsored'] = self.sponsored

        # Gym Park
        if self.park_contains is not None:
            settings['park_contains'] = self.park_contains

        # Geofences
        if self.geofences is not None:
            settings['geofences'] = self.geofences

        # Missing Info
        if self.is_missing_info is not None:
            settings['is_missing_info'] = self.is_missing_info

        return settings

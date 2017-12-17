# Standard Library Imports
import operator
import re
# 3rd Party Imports
# Local Imports
from . import BaseFilter
from PokeAlarm.Utilities import GymUtils as GymUtils


class EggFilter(BaseFilter):
    """ Filter class for limiting which egg trigger a notification. """

    def __init__(self, name, data):
        """ Initializes base parameters for a filter. """
        super(EggFilter, self).__init__(name)

        # Distance
        self.min_dist = self.evaluate_attribute(  # f.min_dist <= e.distance
            event_attribute='distance', eval_func=operator.le,
            limit=BaseFilter.parse_as_type(float, 'min_dist', data))
        self.max_dist = self.evaluate_attribute(  # f.max_dist <= e.distance
            event_attribute='distance', eval_func=operator.ge,
            limit=BaseFilter.parse_as_type(float, 'max_dist', data))

        # Egg Level
        # Level
        self.min_lvl = self.evaluate_attribute(  # f.min_lvl <= e.egg_lvl
            event_attribute='egg_lvl', eval_func=operator.le,
            limit=BaseFilter.parse_as_type(int, 'min_egg_lvl', data))
        self.max_lvl = self.evaluate_attribute(  # f.max_lvl >= e.egg_lvl
            event_attribute='egg_lvl', eval_func=operator.ge,
            limit=BaseFilter.parse_as_type(int, 'max_egg_lvl', data))

        # Gym name
        self.gym_name_matches = self.evaluate_attribute(  # f.gn matches e.gn
            event_attribute='gym_name', eval_func=GymUtils.match_regex_dict,
            limit=BaseFilter.parse_as_set(
                re.compile, 'gym_name_matches', data))

        # Missing Info
        self.ignore_missing = BaseFilter.parse_as_type(
            bool, 'ignore_missing', data)

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
        if self.gym_name_matches is not None:
            settings['gym_name_matches'] = self.gym_name_matches

        # Missing Info
        if self.ignore_missing is not None:
            settings['missing_info'] = self.ignore_missing

        return settings

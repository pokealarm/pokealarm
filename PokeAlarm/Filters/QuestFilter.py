# Standard Library Imports
import operator
# 3rd Party Imports
# Local Imports
from . import BaseFilter
from PokeAlarm.Utilities import GymUtils as GymUtils

class QuestFilter(BaseFilter):
    """ Filter class for limiting which quests trigger a notification. """

    def __init__(self, mgr, name, data):
        """ Initializes base parameters for a filter. """
        super(QuestFilter, self).__init__(mgr, 'quest', name)

        # Distance
        self.min_dist = self.evaluate_attribute(  # f.min_dist <= m.distance
            event_attribute='distance', eval_func=operator.le,
            limit=BaseFilter.parse_as_type(float, 'min_dist', data))
        self.max_dist = self.evaluate_attribute(  # f.max_dist <= m.distance
            event_attribute='distance', eval_func=operator.ge,
            limit=BaseFilter.parse_as_type(float, 'max_dist', data))
            
        # Quest Description
        self.quest_contains = self.evaluate_attribute(  # f.gn matches e.gn
            event_attribute='quest', eval_func=GymUtils.match_regex_dict,
            limit=BaseFilter.parse_as_set(
                GymUtils.create_regex, 'quest_contains', data))
        self.quest_excludes = self.evaluate_attribute(  # f.gn no-match e.gn
            event_attribute='quest',
            eval_func=GymUtils.not_match_regex_dict,
            limit=BaseFilter.parse_as_set(
                GymUtils.create_regex, 'quest_excludes', data))
                
        # Reward Description
        self.reward_contains = self.evaluate_attribute(  # f.gn matches e.gn
            event_attribute='reward', eval_func=GymUtils.match_regex_dict,
            limit=BaseFilter.parse_as_set(
                GymUtils.create_regex, 'reward_contains', data))
        self.reward_excludes = self.evaluate_attribute(  # f.gn no-match e.gn
            event_attribute='reward',
            eval_func=GymUtils.not_match_regex_dict,
            limit=BaseFilter.parse_as_set(
                GymUtils.create_regex, 'reward_excludes', data))

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
                             " Stop filters".format(key))

    def to_dict(self):
        """ Create a dict representation of this Filter. """
        settings = {}

        # Distance
        if self.min_dist is not None:
            settings['min_dist'] = self.min_dist
        if self.max_dist is not None:
            settings['max_dist'] = self.max_dist

        # Geofences
        if self.geofences is not None:
            settings['geofences'] = self.geofences

        # Missing Info
        if self.is_missing_info is not None:
            settings['missing_info'] = self.is_missing_info

        return settings

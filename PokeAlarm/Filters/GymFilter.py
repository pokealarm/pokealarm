# Standard Library Imports
import operator
import re
# 3rd Party Imports
# Local Imports
from . import BaseFilter
from PokeAlarm.Utilities import GymUtils as GymUtils


class GymFilter(BaseFilter):
    """ Filter class for limiting which gyms trigger a notification. """

    def __init__(self, name, data):
        """ Initializes base parameters for a filter. """
        super(GymFilter, self).__init__(name)

        # Distance
        self.min_dist = self.evaluate_attribute(  # f.min_dist <= g.distance
            event_attribute='distance', eval_func=operator.le,
            limit=BaseFilter.parse_as_type(float, 'min_dist', data))
        self.max_dist = self.evaluate_attribute(  # f.max_dist <= g.distance
            event_attribute='distance', eval_func=operator.ge,
            limit=BaseFilter.parse_as_type(float, 'max_dist', data))

        # Team Info
        self.old_team = self.evaluate_attribute(  # f.old_ts contains m.old_t
            event_attribute='old_team_id', eval_func=operator.contains,
            limit=BaseFilter.parse_as_set(
                GymUtils.get_team_id, 'old_teams', data))
        self.new_team = self.evaluate_attribute(  # f.new_ts contains m.new_t
            event_attribute='new_team_id', eval_func=operator.contains,
            limit=BaseFilter.parse_as_set(
                GymUtils.get_team_id, 'new_teams', data))

        # Gym name
        self.gym_name_matches = self.evaluate_attribute(  # f.gn matches g.gn
            event_attribute='gym_name', eval_func=GymUtils.match_regex_dict,
            limit=BaseFilter.parse_as_set(
                re.compile, 'gym_name_matches', data))

        # Missing Info
        self.ignore_missing = BaseFilter.parse_as_type(
            bool, 'ignore_missing', data)

        # Reject leftover parameters
        for key in data:
            raise ValueError("'{}' is not a recognized parameter for"
                             " Gym filters".format(key))

    def to_dict(self):
        """ Create a dict representation of this Filter. """
        settings = {}

        # Distance
        if self.min_dist is not None:
            settings['min_dist'] = self.min_dist
        if self.max_dist is not None:
            settings['max_dist'] = self.max_dist

        # Teams
        if self.old_team is not None:
            settings['old_team'] = self.old_team
        if self.new_team is not None:
            settings['new_team'] = self.new_team

        # Gym Name
        if self.gym_name_matches is not None:
            settings['gym_name_matches'] = self.gym_name_matches

        # Missing Info
        if self.ignore_missing is not None:
            settings['missing_info'] = self.ignore_missing

        return settings

# Standard Library Imports
import operator
import re
# 3rd Party Imports
# Local Imports
from . import Filter
from PokeAlarm.Utilities import Gym as GymUtils


class Gym(Filter):
    """ Filter class for limiting which gyms trigger a notification. """

    def __init__(self, name, data):
        """ Initializes base parameters for a filter. """
        super(Gym, self).__init__(name)

        # Distance
        self.min_dist = self.evaluate_attribute(  # f.min_dist <= g.distance
            event_attribute='distance', eval_func=operator.le,
            limit=Filter.parse_as_type(int, 'min_dist', data))
        self.max_dist = self.evaluate_attribute(  # f.max_dist <= g.distance
            event_attribute='distance', eval_func=operator.ge,
            limit=Filter.parse_as_type(int, 'max_dist', data))

        # Team Info
        self.old_team = self.evaluate_attribute(  # f.min_dist <= g.distance
            event_attribute='old_team_id', eval_func=operator.le,
            limit=Filter.parse_as_type(GymUtils.get_team_id, 'old_team', data))
        self.new_team = self.evaluate_attribute(  # f.max_dist <= g.distance
            event_attribute='from_team_id', eval_func=operator.ge,
            limit=Filter.parse_as_set(GymUtils.get_team_id, 'new_team', data))

        # Gym name
        self.gym_name_matches = self.evaluate_attribute(  # f.gn matches g.gn
            event_attribute='gym_name', eval_func=GymUtils.match_regex_dict,
            limit=Filter.parse_as_set(re.compile, 'gym_name_matches', data))

        # Missing Info
        self.missing_info = Filter.parse_as_type(bool, 'missing_info', data)

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
        if self.missing_info is not None:
            settings['missing_info'] = self.missing_info

        return settings

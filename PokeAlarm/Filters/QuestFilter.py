# Standard Library Imports
import operator
# 3rd Party Imports
# Local Imports
from . import BaseFilter
from PokeAlarm.Utilities import GymUtils as GymUtils, QuestUtils, MonUtils


class QuestFilter(BaseFilter):
    """ Filter class for limiting which quests trigger a notification. """

    def __init__(self, mgr, name, data):
        """ Initializes base parameters for a filter. """
        super(QuestFilter, self).__init__(mgr, 'quest', name)

        # Stop Information
        self.stop_name_contains = self.evaluate_attribute(  # f.gn matches g.gn
            event_attribute='stop_name', eval_func=GymUtils.match_regex_dict,
            limit=BaseFilter.parse_as_set(
                GymUtils.create_regex, 'stop_name_contains', data))
        self.stop_name_excludes = self.evaluate_attribute(  # f.gn no-match e.gn
            event_attribute='stop_name',
            eval_func=GymUtils.not_match_regex_dict,
            limit=BaseFilter.parse_as_set(
                GymUtils.create_regex, 'stop_name_excludes', data))

        # Distance
        self.min_dist = self.evaluate_attribute(  # f.min_dist <= m.distance
            event_attribute='distance', eval_func=operator.le,
            limit=BaseFilter.parse_as_type(float, 'min_dist', data))
        self.max_dist = self.evaluate_attribute(  # f.max_dist <= m.distance
            event_attribute='distance', eval_func=operator.ge,
            limit=BaseFilter.parse_as_type(float, 'max_dist', data))

        # Quest Details
        self.template_contains = self.evaluate_attribute(  # f.gn matches g.gn
            event_attribute='quest_template',
            eval_func=GymUtils.match_regex_dict,
            limit=BaseFilter.parse_as_set(
                GymUtils.create_regex, 'template_contains', data))
        self.template_excludes = self.evaluate_attribute(  # f.gn no-match e.gn
            event_attribute='quest_template',
            eval_func=GymUtils.not_match_regex_dict,
            limit=BaseFilter.parse_as_set(
                GymUtils.create_regex, 'template_excludes', data))

        # Reward Description
        self.reward_types = self.evaluate_attribute(
            event_attribute='reward_type_id', eval_func=operator.contains,
            limit=BaseFilter.parse_as_set(QuestUtils.get_reward_type,
                                          'reward_types', data)
        )
        self.min_reward_amount = self.evaluate_attribute(
            event_attribute='reward_amount', eval_func=operator.le,
            limit=BaseFilter.parse_as_type(int, 'min_reward_amount', data))
        self.max_reward_amount = self.evaluate_attribute(
            event_attribute='reward_amount', eval_func=operator.gt,
            limit=BaseFilter.parse_as_type(int, 'max_reward_amount', data))

        # Monster Rewards
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
        self.forms = self.evaluate_attribute(  # f.forms in m.form_id
            event_attribute='monster_form_id', eval_func=operator.contains,
            limit=BaseFilter.parse_as_set(int, 'form_ids', data))
        self.costumes = self.evaluate_attribute(  # f.costumes in m.costume_id
            event_attribute='monster_costume_id', eval_func=operator.contains,
            limit=BaseFilter.parse_as_set(int, 'costume_ids', data))

        # Item Rewards
        self.item_ids = self.evaluate_attribute(
            event_attribute='item_id', eval_func=operator.contains,
            limit=BaseFilter.parse_as_set(
                QuestUtils.get_item_id, 'items', data))
        self.exclude_item_ids = self.evaluate_attribute(
            event_attribute='item_id',
            eval_func=lambda d, v: not operator.contains(d, v),
            limit=BaseFilter.parse_as_set(
                QuestUtils.get_item_id, 'items_exclude', data))

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
                             " Quest filters".format(key))

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

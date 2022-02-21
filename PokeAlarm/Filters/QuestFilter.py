# Standard Library Imports
import operator
# 3rd Party Imports
# Local Imports
from . import BaseFilter
from PokeAlarm.Utilities import GymUtils as GymUtils, QuestUtils, MonUtils


class QuestFilter(BaseFilter):
    """ Filter class for limiting which quests trigger a notification. """

    def __init__(self, mgr, name, data, geofences_ref=None):
        """ Initializes base parameters for a filter. """
        super(QuestFilter, self).__init__(mgr, 'quest', name, geofences_ref)

        # Stop Information
        self.stop_name_contains = self.evaluate_attribute(  # f.gn matches g.gn
            event_attribute='stop_name', eval_func=GymUtils.match_regex_dict,
            limit=BaseFilter.parse_as_set(
                GymUtils.create_regex, 'stop_name_contains', data))
        self.stop_name_excludes = self.evaluate_attribute(
            # f.gn no-match e.gn
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
        self.task_contains = self.evaluate_attribute(
            event_attribute='quest_task_raw',
            eval_func=GymUtils.match_regex_dict,
            limit=BaseFilter.parse_as_set(
                GymUtils.create_regex, 'task_contains', data))
        self.task_excludes = self.evaluate_attribute(
            event_attribute='quest_task_raw',
            eval_func=GymUtils.not_match_regex_dict,
            limit=BaseFilter.parse_as_set(
                GymUtils.create_regex, 'task_excludes', data))
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
        self.geofences = self.evaluate_geofences(
            BaseFilter.parse_as_list(str, 'geofences', data))
        # Time
        self.evaluate_time(BaseFilter.parse_as_time(
            'min_time', data), BaseFilter.parse_as_time('max_time', data))

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

        # Stop Information
        if self.stop_name_contains is not None:
            settings['stop_name_contains'] = self.stop_name_contains
        if self.stop_name_excludes is not None:
            settings['stop_name_excludes'] = self.stop_name_excludes

        # Distance
        if self.min_dist is not None:
            settings['min_dist'] = self.min_dist
        if self.max_dist is not None:
            settings['max_dist'] = self.max_dist

        # Quest Details
        if self.template_contains is not None:
            settings['template_contains'] = self.template_contains
        if self.template_excludes is not None:
            settings['template_excludes'] = self.template_excludes

        # Reward Description
        if self.reward_types is not None:
            settings['reward_types'] = self.reward_types
        if self.min_reward_amount is not None:
            settings['min_reward_amount'] = self.min_reward_amount
        if self.max_reward_amount is not None:
            settings['max_reward_amount'] = self.max_reward_amount

        # Monster Rewards
        if self.monster_ids is not None:
            settings['monster_ids'] = self.monster_ids
        if self.exclude_monster_ids is not None:
            settings['exclude_monster_ids'] = self.exclude_monster_ids
        if self.forms is not None:
            settings['forms'] = self.forms
        if self.costumes is not None:
            settings['costumes'] = self.costumes

        # Item Rewards
        if self.item_ids is not None:
            settings['item_ids'] = self.item_ids
        if self.exclude_item_ids is not None:
            settings['exclude_item_ids'] = self.exclude_item_ids

        # Geofences
        if self.geofences is not None:
            settings['geofences'] = self.geofences

        # Missing Info
        if self.is_missing_info is not None:
            settings['missing_info'] = self.is_missing_info

        return settings

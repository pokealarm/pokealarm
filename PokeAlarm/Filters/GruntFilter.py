# Standard Library Imports
import operator
# 3rd Party Imports
# Local Imports
from . import BaseFilter
from PokeAlarm.Utilities import MonUtils
from PokeAlarm.Utils import get_gender_sym, match_items_in_array, \
    get_weather_id, weather_id_is_boosted


class GruntFilter(BaseFilter):
    """ Filter class for limiting which invasions trigger a notification. """

    def __init__(self, mgr, name, data, geofences_ref=None):
        """ Initializes base parameters for a filter. """
        super(GruntFilter, self).__init__(mgr, 'invasion', name, geofences_ref)

        # Grunts
        self.grunt_ids = self.evaluate_attribute(
            event_attribute='grunt_type_id', eval_func=operator.contains,
            limit=BaseFilter.parse_as_set(
                int, 'grunt_ids', data))

        # Exclude Grunts
        self.exclude_grunt_ids = self.evaluate_attribute(
            event_attribute='grunt_type_id',
            eval_func=lambda d, v: not operator.contains(d, v),
            limit=BaseFilter.parse_as_set(
                int, 'grunts_exclude', data))

        # Monster types
        self.type_ids = self.evaluate_attribute(
            event_attribute='mon_type_id', eval_func=operator.contains,
            limit=BaseFilter.parse_as_list(
                MonUtils.get_type_id, 'types', data))

        # Monster ID
        self.monster_ids = self.evaluate_attribute(  #
            event_attribute='reward_mon_ids', eval_func=match_items_in_array,
            limit=BaseFilter.parse_as_set(
                MonUtils.get_monster_id, 'monsters', data))

        # Exclude Monsters
        self.exclude_monster_ids = self.evaluate_attribute(  #
            event_attribute='reward_mon_ids',
            eval_func=lambda d, v: not match_items_in_array(d, v),
            limit=BaseFilter.parse_as_set(
                MonUtils.get_monster_id, 'monsters_exclude', data))

        # Gender
        self.genders = self.evaluate_attribute(  # f.genders contains m.gender
            event_attribute='gender', eval_func=match_items_in_array,
            limit=BaseFilter.parse_as_set(
                get_gender_sym, 'grunt_genders', data))

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

        # Weather
        self.weather_ids = self.evaluate_attribute(
            event_attribute='weather_id', eval_func=operator.contains,
            limit=BaseFilter.parse_as_set(get_weather_id, 'weather', data))
        self.boosted_weather_ids = self.evaluate_attribute(
            event_attribute='boosted_weather_id', eval_func=operator.contains,
            limit=BaseFilter.parse_as_set(
                get_weather_id, 'boosted_weather', data))
        self.boosted_weather = self.evaluate_attribute(
            event_attribute='boosted_weather_id',
            eval_func=weather_id_is_boosted,
            limit=BaseFilter.parse_as_type(bool, 'is_boosted_weather', data))

        # Geofences
        self.geofences = self.evaluate_geofences(
            geofences=BaseFilter.parse_as_list(str, 'geofences', data),
            exclude_mode=False)
        self.exclude_geofences = self.evaluate_geofences(
            geofences=BaseFilter.parse_as_list(str, 'exclude_geofences', data),
            exclude_mode=True)

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
                             " Invasion filters".format(key))

    def to_dict(self):
        """ Create a dict representation of this Filter. """
        settings = {}

        # Grunts
        if self.grunt_ids is not None:
            settings['grunt_ids'] = self.grunt_ids

        # Cosmetic
        if self.genders is not None:
            settings['genders'] = self.genders

        # Distance
        if self.min_dist is not None:
            settings['min_dist'] = self.min_dist
        if self.max_dist is not None:
            settings['max_dist'] = self.max_dist

        # Geofences
        if self.geofences is not None:
            settings['geofences'] = self.geofences
        if self.exclude_geofences is not None:
            settings['exclude_geofences'] = self.exclude_geofences

        # Missing Info
        if self.is_missing_info is not None:
            settings['missing_info'] = self.is_missing_info

        return settings

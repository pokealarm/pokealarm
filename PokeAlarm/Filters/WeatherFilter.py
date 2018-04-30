# Standard Library Imports
import operator
# 3rd Party Imports
# Local Imports
from . import BaseFilter
from PokeAlarm.Utilities import WeatherUtils as WeatherUtils
from PokeAlarm.Utils import get_weather_id


class WeatherFilter(BaseFilter):
    """ Filter class for limiting which stops trigger a notification. """

    def __init__(self, mgr, name, data):
        """ Initializes base parameters for a filter. """
        super(WeatherFilter, self).__init__(mgr, 'weather', name)

        # Distance to center of cell
        self.min_dist = self.evaluate_attribute(  # f.min_dist <= m.distance
            event_attribute='distance', eval_func=operator.le,
            limit=BaseFilter.parse_as_type(float, 'min_dist', data))
        self.max_dist = self.evaluate_attribute(  # f.max_dist <= m.distance
            event_attribute='distance', eval_func=operator.ge,
            limit=BaseFilter.parse_as_type(float, 'max_dist', data))

        # Weather filters
        self.weather = self.evaluate_attribute(
            event_attribute='weather_id', eval_func=operator.contains,
            limit=BaseFilter.parse_as_set(
                get_weather_id, 'weather', data))
        self.day_or_night = self.evaluate_attribute(
            event_attribute='day_or_night_id', eval_func=operator.contains,
            limit=BaseFilter.parse_as_set(
                WeatherUtils.get_day_or_night_id, 'day_or_night', data))
        self.severity = self.evaluate_attribute(
            event_attribute='severity_id', eval_func=operator.contains,
            limit=BaseFilter.parse_as_set(
                WeatherUtils.get_severity_id, 'severity', data))

        # Geofences
        self.geofences = BaseFilter.parse_as_list(str, 'geofences', data)

        # Custom DTS
        self.custom_dts = BaseFilter.parse_as_dict(
            str, str, 'custom_dts', data)

        # Reject leftover parameters
        for key in data:
            raise ValueError("'{}' is not a recognized parameter for"
                             " Weather filters".format(key))

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

        # Weather
        if self.weather is not None:
            settings['weather'] = self.weather
        if self.day_or_night is not None:
            settings['day_or_night'] = self.day_or_night
        if self.severity is not None:
            settings['severity'] = self.severity

        return settings

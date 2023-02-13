# Standard Library Imports
import operator

# 3rd Party Imports
# Local Imports
from . import BaseFilter
from PokeAlarm.Utilities import StopUtils as StopUtils


class StopFilter(BaseFilter):
    """Filter class for limiting which stops trigger a notification."""

    def __init__(self, mgr, name, data, geofences_ref=None):
        """Initializes base parameters for a filter."""
        super(StopFilter, self).__init__(mgr, "stop", name, geofences_ref)

        # Lures
        self.lure_ids = self.evaluate_attribute(
            event_attribute="lure_type_id",
            eval_func=operator.contains,
            limit=BaseFilter.parse_as_set(StopUtils.get_lure_id, "lures", data),
        )

        # Exclude Lures
        self.exclude_lure_ids = self.evaluate_attribute(
            event_attribute="lure_type_id",
            eval_func=lambda d, v: not operator.contains(d, v),
            limit=BaseFilter.parse_as_set(StopUtils.get_lure_id, "lures_exclude", data),
        )

        # Distance
        self.min_dist = self.evaluate_attribute(  # f.min_dist <= m.distance
            event_attribute="distance",
            eval_func=operator.le,
            limit=BaseFilter.parse_as_type(float, "min_dist", data),
        )
        self.max_dist = self.evaluate_attribute(  # f.max_dist <= m.distance
            event_attribute="distance",
            eval_func=operator.ge,
            limit=BaseFilter.parse_as_type(float, "max_dist", data),
        )

        # Time Left
        self.min_time_left = self.evaluate_attribute(
            # f.min_time_left <= r.time_left
            event_attribute="time_left",
            eval_func=operator.le,
            limit=BaseFilter.parse_as_type(int, "min_time_left", data),
        )
        self.max_time_left = self.evaluate_attribute(
            # f.max_time_left >= r.time_left
            event_attribute="time_left",
            eval_func=operator.ge,
            limit=BaseFilter.parse_as_type(int, "max_time_left", data),
        )

        # Geofences
        self.geofences = self.evaluate_geofences(
            geofences=BaseFilter.parse_as_list(str, "geofences", data),
            exclude_mode=False,
        )
        self.exclude_geofences = self.evaluate_geofences(
            geofences=BaseFilter.parse_as_list(str, "exclude_geofences", data),
            exclude_mode=True,
        )

        # Time
        self.evaluate_time(
            BaseFilter.parse_as_time("min_time", data),
            BaseFilter.parse_as_time("max_time", data),
        )

        # Custom DTS
        self.custom_dts = BaseFilter.parse_as_dict(str, str, "custom_dts", data)

        # Missing Info
        self.is_missing_info = BaseFilter.parse_as_type(bool, "is_missing_info", data)

        # Reject leftover parameters
        for key in data:
            raise ValueError(f"'{key}' is not a recognized parameter for Stop filters")

    def to_dict(self):
        """Create a dict representation of this Filter."""
        settings = {}
        # Lures
        if self.lure_ids is not None:
            settings["lure_ids"] = self.lure_ids

        # Distance
        if self.min_dist is not None:
            settings["min_dist"] = self.min_dist
        if self.max_dist is not None:
            settings["max_dist"] = self.max_dist

        # Geofences
        if self.geofences is not None:
            settings["geofences"] = self.geofences
        if self.exclude_geofences is not None:
            settings["exclude_geofences"] = self.exclude_geofences

        # Missing Info
        if self.is_missing_info is not None:
            settings["missing_info"] = self.is_missing_info

        return settings

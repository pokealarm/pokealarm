# Standard Library Imports
import logging
from datetime import datetime, timedelta

# 3rd Party Imports
# Local Imports
from PokeAlarm import Unknown

log = logging.getLogger("Filter")


class BaseFilter(object):
    """Abstract class representing details related to different events."""

    def __init__(self, mgr, kind, name, geofences_ref):
        """Initializes base parameters for a filter."""

        # Logger for rejecting items
        self._name = name
        self._type = kind

        self._log = mgr.get_child_logger("filters")

        # Dict representation for the filter
        self._settings = {}

        # Functions for checking set parameters
        self._check_list = []

        # Missing Info
        self.is_missing_info = None

        # Geofence references (loaded from the local file)
        self.geofences_ref = geofences_ref

    def __str__(self):
        return str(self.to_dict())

    def to_dict(self):
        """Create a dict representation of this Event."""
        raise NotImplementedError("This is an abstract method.")

    def check_event(self, event):
        missing = False  # Event is missing no info to start
        for check in self._check_list:
            result = check(self, event)
            if result is False:
                return False
            elif Unknown.is_(result):
                missing = True  # Mark Event as missing info
        # Do a special check for is missing_info is set
        if self.is_missing_info is not None and missing != self.is_missing_info:
            self.reject(event, "missing_info", missing, self.is_missing_info)
            return False
        self.accept(event)
        return True

    def reject(self, event, attr_name, value, required):
        """Log the reason for rejecting the Event."""
        self._log.info("'%s' %s rejected by '%s'", event.name, self._type, self._name)
        self._log.debug("%s incorrect: (%s to %s)", attr_name, value, required)

    def accept(self, event):
        """Log that the Event was accepted."""
        self._log.info("'%s' %s accepted by '%s'", event.name, self._type, self._name)

    def evaluate_attribute(self, limit, eval_func, event_attribute):
        """Evaluates a parameter and generate a check if needed."""
        if limit is None:
            return None  # limit not set

        # Create a function to compare the event vs the limit
        check = CheckFunction(limit, eval_func, event_attribute)

        # Add check function to our list
        self._check_list.append(check)
        return limit

    def evaluate_time(self, min_time, max_time):
        if min_time is None and max_time is None:
            return None  # limit not set

        if min_time is None:
            min_time = 0.0
        if max_time is None:
            max_time = 60.0 * 60.0 * 24.0

        # Create a function to compare the current time to time range
        check = CheckTime(min_time, max_time)

        # Add check function to our list
        self._check_list.append(check)

    def evaluate_geofences(self, geofences, exclude_mode):
        if geofences is None:
            return None  # limit not set

        # Create a function to compare the current time to time range
        check = CheckGeofence(geofences, self.geofences_ref, exclude_mode)

        # Add check function to our list
        self._check_list.append(check)

    @staticmethod
    def parse_as_type(kind, param_name, data):
        """Parse a parameter as a certain type."""
        try:
            value = data.pop(param_name, None)
            if value is None:
                return None
            else:
                return kind(value)
        except Exception:
            raise ValueError(
                'Unable to interpret the value "{}" as a '.format(value)
                + 'valid {} for parameter {}.", '.format(kind, param_name)
            )

    @staticmethod
    def parse_as_list(value_type, param_name, data):
        """Parse and convert a list of values into a list."""
        # Validate Input
        values = data.pop(param_name, None)
        if values is None or len(values) == 0:
            return None
        if not isinstance(values, list):
            raise ValueError(
                'The "{0}" parameter must formatted as a list containing '
                'different values. Example: "{0}": '
                '[ "value1", "value2", "value3" ] '.format(param_name)
            )
        # Generate Allowed Set
        allowed = []
        for value in values:
            # Value type should throw the correct error
            allowed.append(value_type(value))
        return allowed

    @staticmethod
    def parse_as_set(value_type, param_name, data):
        """Parse and convert a list of values into a set."""
        # Validate Input
        values = data.pop(param_name, None)
        if values is None or len(values) == 0:
            return None
        if not isinstance(values, list):
            raise ValueError(
                'The "{0}" parameter must formatted as a list containing '
                'different values. Example: "{0}": '
                '[ "value1", "value2", "value3" ] '.format(param_name)
            )
        # Generate Allowed Set
        allowed = set()
        for value in values:
            # Value type should throw the correct error
            allowed.add(value_type(value))
        return allowed

    @staticmethod
    def parse_as_nested_set(value_type, param_name, data):
        """Parse and convert a list of values into a set."""
        # Validate Input
        values = data.pop(param_name, None)
        if values is None or len(values) == 0:
            return None
        if not isinstance(values, list):
            raise ValueError(
                'The "{0}" parameter must formatted as a list containing '
                'different values. Example: "{0}": '
                '[ "value1", "value2", "value3" ] '.format(param_name)
            )
        # Generate Allowed Set
        allowed = set()
        for value in values:
            # Value type should throw the correct error
            types = value_type(value)
            if isinstance(types, list):
                for nested_type in types:
                    allowed.add(nested_type)
            else:
                allowed.add(value_type(value))
        return allowed

    @staticmethod
    def parse_as_time(param_name, data):
        """Parse a time with X:XX format (24h) and convert in seconds"""
        try:
            value = data.pop(param_name, None)
            if value is None:
                return None
            else:
                try:
                    absolute_time_sec = datetime.strptime(value, "%H:%M")
                    return (
                        absolute_time_sec - absolute_time_sec.replace(hour=0, minute=0)
                    ).total_seconds()
                except Exception:
                    raise ValueError(
                        'Unable to interpret the value "{}" as a '.format(value)
                        + 'valid X:XX format for parameter {}.", '.format(param_name)
                    )
        except Exception:
            raise ValueError(
                'Unable to interpret the value "{}" as a '.format(value)
                + 'valid  X:XX format for parameter {}.", '.format(param_name)
            )

    @staticmethod
    def parse_as_dict(key_type, value_type, param_name, data):
        """Parse and convert a dict of values into a specific types."""
        values = data.pop(param_name, {})
        if not isinstance(values, dict):
            raise ValueError(
                'The "{0}" parameter must formatted as a dict containing '
                'key-value pairs. Example: "{0}": '
                '{{ "key1": "value1", "key2": "value2" }}'.format(param_name)
            )
        out = {}
        for k, v in values.items():
            try:
                out[key_type(k)] = value_type(v)
            except Exception:
                raise ValueError(
                    'There was an error while parsing \'"{}": "{}"\' in '
                    'parameter name "{}"'.format(k, v, param_name)
                )
        return out


class CheckFunction(object):
    """Function used to check if an event passes or not."""

    def __init__(self, limit, eval_func, attr_name):
        self._limit = limit
        self._eval_func = eval_func
        self._attr_name = attr_name

    def __call__(self, filtr, event):
        value = getattr(event, self._attr_name)  # event.event_attr
        if type(value) == list:
            if Unknown.is_(*value):
                return Unknown.TINY  # Cannot check - missing attribute
        elif Unknown.is_(value):
            return Unknown.TINY  # Cannot check - missing attribute
        result = self._eval_func(self._limit, value)  # compare value to limit

        if result is False:  # Log rejection
            filtr.reject(event, self._attr_name, value, self._limit)

        return result


class CheckTime(object):
    """Function used to check if a timestamp passes or not."""

    def __init__(self, min_time, max_time):
        self._min_time = min_time
        self._max_time = max_time
        self._override_time = None

    def __call__(self, filtr, event):
        if self._override_time is not None:
            current_time = self._override_time
        else:
            now = datetime.now()
            current_time = (
                now - now.replace(hour=0, minute=0, second=0)
            ).total_seconds()
        if self._min_time <= self._max_time:
            result = self._min_time <= current_time and current_time <= self._max_time
        else:
            result = self._min_time <= current_time or current_time <= self._max_time

        if result is False:  # Log rejection
            filtr.reject(
                event,
                "time range",
                str(timedelta(seconds=current_time)),
                [
                    str(timedelta(seconds=self._min_time)),
                    str(timedelta(seconds=self._max_time)),
                ],
            )

        return result

    def override_time(self, current_time):
        """For unit tests purposes"""
        absolute_time_sec = datetime.strptime(current_time, "%H:%M")
        self._override_time = (
            absolute_time_sec - absolute_time_sec.replace(hour=0, minute=0)
        ).total_seconds()


class CheckGeofence(object):
    """Function used to check if an event passes or not."""

    def __init__(self, limit, geofences_ref, exclude_mode):
        self._limit = limit
        self._geofences_ref = geofences_ref
        self._exclude_mode = exclude_mode

    def __call__(self, filtr, event):
        lat = getattr(event, "lat")
        lng = getattr(event, "lng")

        if Unknown.is_(lat) or Unknown.is_(lng):
            return Unknown.TINY  # Cannot check - missing attribute

        if self._geofences_ref is None:  # no local geofence file
            return True

        targets = self._limit
        if len(targets) == 1 and "all" in targets:
            targets = self._geofences_ref.keys()
        for name in targets:
            gf = self._geofences_ref.get(name)
            if not gf:  # gf doesn't exist :'(
                filtr.reject(event, "geofence name", f"{name} not", "geofence list")
            elif gf.contains(lat, lng):  # event in gf
                if self._exclude_mode:
                    filtr.reject(
                        event, "location", f"{lat},{lng}", f"'{name}' geofence"
                    )
                    return False
                else:
                    event.geofence = name  # Set the geofence for dts
                    return True
            else:  # event not in gf
                filtr.reject(
                    event, "location", f"{lat},{lng} not", f"'{name}' geofence"
                )
        if self._exclude_mode:
            return True
        else:
            return False

    def override_geofences_ref(self, geofences_ref):
        """For unit tests purposes"""
        self._geofences_ref = geofences_ref

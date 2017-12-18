# Standard Library Imports
import logging
import json
# 3rd Party Imports
# Local Imports
from PokeAlarm import Unknown


class BaseFilter(object):
    """ Abstract class representing details related to different events. """

    def __init__(self, name):
        """ Initializes base parameters for a filter. """

        # Logger for rejecting items
        self._log = logging.getLogger(name)

        # Dict representation for the filter
        self._settings = {}

        # Functions for checking set parameters
        self._check_list = []

        # Missing Info
        self.missing_info = None

    def to_dict(self):
        """ Create a dict representation of this Event. """
        raise NotImplementedError("This is an abstract method.")

    def to_string(self):
        return json.dumps(self.to_dict(), indent=4, sort_keys=True)

    def check_event(self, event):
        missing = False  # Is the event missing needed info?
        for check in self._check_list:
            result = check(self, event)
            if result is False:
                return False
            elif Unknown.is_(result):
                missing = True
        # Do a special check for is missing_info is set
        if self.missing_info is not None and missing == self.missing_info:
            self.reject(event, "needed information was missing.")
            return False
        return True

    def reject(self, event, reason):
        """ Log the reason for rejecting the Event. """
        self._log.info("%s rejected: %s", event.name, reason)

    def evaluate_attribute(self, limit, eval_func, event_attribute):
        """ Evaluates a parameter and generate a check if needed. """
        if limit is None:
            return None  # limit not set

        # Create a function to compare the event vs the limit
        def check(f, e):  # filter.check(event)
            value = getattr(e, event_attribute)  # e.event_attribute
            if Unknown.is_(value):
                return Unknown.TINY  # Cannot check - missing attribute
            result = eval_func(limit, value)  # compare value to limit
            if result is False:
                f.reject(  # Log rejection
                    e, "{} incorrect ({} to {})".format(
                        event_attribute, value, limit))
            return result
        # Add check function to our list
        self._check_list.append(check)
        return limit

    @staticmethod
    def parse_as_type(kind, param_name, data):
        """ Parse a parameter as a certain type. """
        try:
            value = data.pop(param_name, None)
            if value is None:
                return None
            else:
                return kind(value)
        except Exception:
            raise ValueError(
                'Unable to interpret the value "{}" as a '.format(value) +
                'valid {} for parameter {}.", '.format(kind, param_name))

    @staticmethod
    def parse_as_set(value_type, param_name, data):
        """ Parse and convert a list of values into a set."""
        # Validate Input
        values = data.pop(param_name, None)
        if values is None or len(values) == 0:
            return None
        if not isinstance(values, list):
            raise ValueError(
                'The "{0}" parameter must formatted as a list containing '
                'different values. Example: "{0}": '
                '[ "value1", "value2", "value3" ] '.format(param_name))
        # Generate Allowed Set
        allowed = set()
        for value in values:
            # Value type should throw the correct error
            allowed.add(value_type(value))
        return allowed

    @staticmethod
    def parse_as_dict(key_type, value_type, param_name, data):
        """ Parse and convert a dict of values into a specific types."""
        values = data.pop(param_name, {})
        if not isinstance(values, dict):
            raise ValueError(
                'The "{0}" parameter must formatted as a dict containing '
                'key-value pairs. Example: "{0}": '
                '{{ "key1": "value1", "key2": "value2" }}'.format(param_name))
        out = {}
        for k, v in values.iteritems():
            try:
                out[key_type(k)] = value_type(v)
            except Exception:
                raise ValueError(
                    'There was an error while parsing \'"{}": "{}"\' in '
                    'parameter name "{}"'.format(k, v, param_name))
        return out

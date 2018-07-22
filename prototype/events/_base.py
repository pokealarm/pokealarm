# -*- coding: utf-8 -*-

"""
pokealarm._base
~~~~~~~~~~~~~~~~

This module contains the base class and meta class for creating new Event
types.
"""

# Standard Library Imports
import logging
from typing import List, Mapping, Optional  # noqa F401
# 3rd Party Imports
import six
from future.utils import iteritems
# Local Imports


log = logging.getLogger(__name__)


class EventAttr(object):
    """
    An attribute extracted from a dict during Event initialization.
    """

    def __init__(self, keys, validator, required=False, default=None):
        # type: (List[str], function, Optional) -> None
        self.keys = keys
        self.validator = validator
        self.required = required
        self.default = default

    def __call__(self, obj, name, data):
        # type: (Event, str, Mapping[str, object]) -> None
        # Extract value by first valid key in data
        gen = ((k, data[k]) for k in self.keys if data.get(k) is not None)
        key, value = next(gen, (name, self.default))
        if self.required and value is None:
            raise ValueError(
                "Missing required attribute {}.".format(name))
        try:
            if value is not None:
                value = self.validator(value)
            setattr(obj, name, value)
        except Exception:
            log.warning("Error occurred while attempted to validate "
                        "{} with {}".format(key, type(self.validator)))
            raise


class _MetaEvent(type):
    """
    Metaclass for Events.

    During an Event class creation, all _EventAttr's are gathered into a dict
    in the '_event_attr' function. _EventAttr's are used during object
    initialization to set attributes extracted from dict.
    """

    def __new__(mcs, name, bases, dct):
        # Collect all _EventAttr into _event_attr dict
        dct['_event_attr'] = {
            k: dct.pop(k)
            for k in dct.keys() if isinstance(dct[k], EventAttr)}
        return super(_MetaEvent, mcs).__new__(mcs, name, bases, dct)


@six.add_metaclass(_MetaEvent)
class Event(object):
    """
    Basic object representation of an Event.

    Event classes should inherit this class in order to assemble correctly.
    """

    _event_attr = {}

    def __init__(self, data):
        # type: (Mapping) -> None
        # Use the classes EventAttr's to set attributes from dict
        for name, event_attr in iteritems(self._event_attr):
            event_attr(self, name, data)

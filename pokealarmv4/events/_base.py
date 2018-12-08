"""
pokealarmv4._base
~~~~~~~~~~~~~~~~

This module contains base classes for the creation of the Events module.
"""

from typing import Any, Callable, List, Mapping, NamedTuple, Optional


class EventAttr(NamedTuple):
    """
    EvenAttr is a helper class for define EventAttr. When defined in an Event
    class, they will be used to automatically convert dict values into object
    attributes during object initialization.
    """
    keys: List[str]
    validate: Callable
    required: bool = False
    default: Optional[Any] = None

    def extract(self, name: str, data: Mapping):
        # Use a generator to retrieve first non-None answer
        gen = (data[k] for k in self.keys if data.get(k) is not None)
        value = next(gen, self.default)
        if self.required and value is None:
            raise ValueError(
                f'Missing required attribute {name} under any of the following'
                f' keys: {self.keys}')
        if value is not None:
            value = self.validate(value)
        return value


class MetaEvent(type):
    """
    Metaclass for events.Event. Automates initialization of Event objects from
    a given dict..
    """

    def __new__(mcs, name, bases, dct):
        # Move any event attributes into `_event_attrs` for later reference
        dct['_event_attrs'] = {
            k: dct.pop(k)
            for k in list(dct.keys()) if isinstance(dct[k], EventAttr)
        }
        return super(MetaEvent, mcs).__new__(mcs, name, bases, dct)


class Event(object, metaclass=MetaEvent):
    """
    Base class for representing events. Uses EventAttr to extract attributes
    from a given dict.
    """

    _event_attrs = {}

    def __init__(self, data: Mapping):
        # Use the classes EventAttr's to set attributes from dict input
        for name, attr in self._event_attrs.items():
            setattr(self, name, attr.extract(name, data))

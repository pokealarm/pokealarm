"""
pokealarmv4._base
~~~~~~~~~~~~~~~~

This module contains base classes for the creation of the Events module.
"""
# Standard Library Imports
from abc import ABCMeta, abstractmethod
from typing import Any, Callable, List, Mapping, NamedTuple, Optional
# 3rd Party Imports
# Local Imports


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
            try:
                value = self.validate(value)
            except TypeError as ex:
                raise TypeError(
                    f"Unable to validate '{value}' with '{self.validate}'."
                    f"\n{ex}")
        return value


class EventType(ABCMeta):
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
        return super(EventType, mcs).__new__(mcs, name, bases, dct)


class Event(object, metaclass=EventType):
    """
    Base class for representing events. Uses EventAttr to extract attributes
    from a given dict.
    """

    _event_attrs: Mapping[str, EventAttr] = {}

    def __init__(self, data: Mapping):
        # Use the classes EventAttr's to set attributes from dict input
        for name, attr in self._event_attrs.items():
            setattr(self, name, attr.extract(name, data))

    @property
    @abstractmethod
    def id(self) -> int:
        """
        Returns a unique id that identifies the in-game object around which the
        event occurs.
        """
        pass

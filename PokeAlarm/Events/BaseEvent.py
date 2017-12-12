# Standard Library Imports
import logging
# 3rd Party Imports
# Local Imports


class Event(object):
    """ Abstract class representing details related to different events. """

    def __init__(self, kind):
        """ Initializes base parameters for an event. """
        self._log = logging.getLogger(kind)

    def generate_dts(self, locale):
        """ Return a dict with all the DTS for this event. """
        raise NotImplementedError("This is an abstract method.")

    @classmethod
    def check_for_none(cls, cast, val, default):
        """ Returns val as type cast or default if val is None """
        return cast(val) if val is not None else default

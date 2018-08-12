# -*- coding: utf-8 -*-

"""
pokealarm.events.stop
~~~~~~~~~~~~~~~~

This module contains classes for managing changes to pokestops.
"""

# Standard Library Imports
from datetime import datetime
# 3rd Party Imports
# Local Imports
from _base import Event, EventAttr


class Stop(Event):
    """
    Object representation of a change to a stop.
    """

    # Location
    lat = EventAttr(['latitude'], float)  # type: float
    lng = EventAttr(['longitude'], float)  # type: float
    # Completed by Manager
    distance = None  # type: float
    direction = None  # type: str

    # Identification
    stop_id = EventAttr(['pokestop_id'], str, required=True)  # type: str

    # Expiration
    expiration = EventAttr(
        ['lure_expiration'], datetime.utcfromtimestamp)  # type: datetime

    @property
    def time_left(self):
        # type: () -> float
        if not self.expiration:
            return None
        return (self.expiration - datetime.utcnow()).total_seconds()

"""
pokealarmv4.events.stop
~~~~~~~~~~~~~~~~

This module contains classes for managing changes to stop points.
"""
# Standard Library Imports
from datetime import datetime
# 3rd Party Imports
# Local Imports
from ._base import Event, EventAttr
from typing import Optional


class Stop(Event):
    """
    Object representation of a change to a stop.
    """

    # Identification
    stop_id: str = EventAttr(['pokestop_id'], str, required=True)

    @property
    def id(self) -> int:
        return hash(self.stop_id)

    # Location
    lat: float = EventAttr(['latitude'], float, required=True)
    lng: float = EventAttr(['longitude'], float, required=True)

    # Expiration
    expiration: datetime = EventAttr(
        ['lure_expiration'], datetime.utcfromtimestamp)

    @property
    def time_left(self) -> Optional[float]:
        if not self.expiration:
            return None
        return (self.expiration - datetime.utcnow()).total_seconds()

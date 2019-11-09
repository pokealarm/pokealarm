"""
pokealarmv4.events.grunt
~~~~~~~~~~~~~~~~

This module contains classes for managing Team Rocket invasions.
"""
# Standard Library Imports
from datetime import datetime
# 3rd Party Imports
# Local Imports
from ._base import Event, EventAttr
from typing import Optional
from PokeAlarm.Utilities.StopUtils import get_grunt_gender


class Grunt(Event):
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
        ['incident_expiration', 'incident_expire_timestamp'],
        datetime.utcfromtimestamp)

    # Grunt details
    type_id: EventAttr(
        ['incident_grunt_type', 'grunt_type'], int, required=True)

    @property
    def gender(self) -> int:
        return get_grunt_gender(self.type_id)

    @property
    def time_left(self) -> Optional[float]:
        if not self.expiration:
            return None
        return (self.expiration - datetime.utcnow()).total_seconds()

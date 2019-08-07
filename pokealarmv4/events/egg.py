"""
pokealarm.events.egg
~~~~~~~~~~~~~~~~

This module contains classes for managing changes to Eggs in-game.
"""

# Standard Library Imports
from __future__ import absolute_import, unicode_literals
from datetime import datetime
# 3rd Party Imports
# Local Imports
from ._base import Event, EventAttr


class Egg(Event):
    """
    Object representation of an Egg, which is an early indicator of a raid.
    """

    # Identification
    gym_id: str = EventAttr(['gym_id', 'id'], str, required=True)

    @property
    def id(self) -> int:
        return hash(self.gym_id)

    # Location
    lat: float = EventAttr(['latitude'], float, required=True)
    lng: float = EventAttr(['longitude'], float, required=True)

    # Gym Info
    gym_name: str = EventAttr(['name'], str)
    gym_description: str = EventAttr(['description'], str)
    gym_image: str = EventAttr(['url'], str)

    team_id: int = EventAttr(['team_id', 'team'], int)
    weather_id: int = EventAttr(['weather'], int)
    sponsor_id: int = EventAttr(['sponsor'], int)
    park_name: str = EventAttr(['park'], str)

    # Time Remaining
    hatch_time: datetime = EventAttr(
        ['start', 'raid_begin'], datetime.utcfromtimestamp, required=True)
    raid_end: datetime = EventAttr(
        ['end', 'raid_end'], datetime.utcfromtimestamp, required=True)

    @property
    def time_left(self) -> float:
        return (self.hatch_time - datetime.utcnow()).total_seconds()

    # Egg Info
    egg_lvl: int = EventAttr(['level'], int, default=0)

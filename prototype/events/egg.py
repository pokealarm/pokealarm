# -*- coding: utf-8 -*-
"""
pokealarm.events.egg
~~~~~~~~~~~~~~~~

This module contains classes for managing changes to Eggs ingame.
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

    # Location
    lat = EventAttr(['latitude'], float)  # type: float
    lng = EventAttr(['longitude'], float)  # type: float
    weather_id = EventAttr(['weather'], int)  # type: int
    # Completed by Manager
    distance = None  # type: float
    direction = None  # type: str

    # Gym Info
    gym_id = EventAttr(['gym_id', 'id'], str, required=True)  # type: str

    gym_name = EventAttr(['name'], str)  # type: str
    gym_description = EventAttr(['description'], str)  # type: str
    gym_image = EventAttr(['url'], str)  # type: str
    team_id = EventAttr(['team_id', 'team'], int)  # type: str

    sponsor_id = EventAttr(['sponsor'], int)  # type: int
    park = EventAttr(['park'], str)  # type: str

    # Time Remaining
    hatch_time = EventAttr(  # type: datetime
        ['start', 'raid_begin'], datetime.utcfromtimestamp, required=True)
    raid_end = EventAttr(  # type: datetime
        ['end', 'raid_end'], datetime.utcfromtimestamp, required=True)

    @property
    def time_left(self):
        # type: () -> float
        return (self.hatch_time - datetime.utcnow()).total_seconds()

    # Egg Info
    egg_lvl = EventAttr(['level'], int, default=0)  # type: int

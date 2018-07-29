# -*- coding: utf-8 -*-

"""
pokealarm.events.raid
~~~~~~~~~~~~~~~~

This module contains classes for managing changes to a Raid ingame.
"""

# Standard Library Imports
from datetime import datetime
# 3rd Party Imports
# Local Imports
from _base import Event, EventAttr


class Raid(Event):
    """
    Object representation of an ingame Raid.
    """

    # Location
    lat = EventAttr(['latitude'], float)  # type: float
    lng = EventAttr(['longitude'], float)  # type: float
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
    raid_end = EventAttr(  # type: datetime
        ['end', 'raid_end'], datetime.utcfromtimestamp, required=True)

    @property
    def time_left(self):
        # type: () -> float
        return (self.raid_end - datetime.utcnow()).total_seconds()

    # Monster Info
    raid_lvl = EventAttr(['level'], int, required=True)  # type: int
    monster_id = EventAttr(['pokemon_id'], int, required=True)  # type: int
    cp = EventAttr(['cp'], int, required=True)  # type: int

    form_id = EventAttr(['form'], int, default=0)  # type: int
    costume_id = EventAttr(['costume'], int, default=0)  # type: int

    quick_id = EventAttr(['move_1'], int)  # type: int
    charge_id = EventAttr(['move_2'], int)  # type: int

    # Weather Info
    weather_id = EventAttr(['weather'], int)  # type: int

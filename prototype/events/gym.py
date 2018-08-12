# -*- coding: utf-8 -*-

"""
pokealarm.events.gym
~~~~~~~~~~~~~~~~

This module contains classes for managing changes to Gyms ingame.
"""

# Standard Library Imports
# 3rd Party Imports
# Local Imports
from _base import Event, EventAttr


class Gym(Event):
    """
    Object representation of an ingame Gym.
    """

    # Location
    lat = EventAttr(['latitude'], float)  # type: float
    lng = EventAttr(['longitude'], float)  # type: float
    # Completed by Manager
    distance = None  # type: float
    direction = None  # type: str

    # Gym Info
    gym_id = EventAttr(['gym_id', 'id'], str, required=True)  # type: str
    team_id = EventAttr(['team_id', 'team'], int, required=True)  # type: int

    gym_name = EventAttr(['name'], str)  # type: str
    gym_description = EventAttr(['description'], str)  # type: str
    gym_image = EventAttr(['url'], str)  # type: str

    open_slots = EventAttr(['slots_available'], int)  # type: int

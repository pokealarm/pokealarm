"""
pokealarmv4.events.gym
~~~~~~~~~~~~~~~~

This module contains classes for managing changes to Gyms in-game.
"""

# Standard Library Imports
# 3rd Party Imports
# Local Imports
from ._base import Event, EventAttr


class Gym(Event):
    """
    Object representation of an ingame Gym.
    """

    # Identification
    gym_id: str = EventAttr(['gym_id', 'id'], str, required=True)

    # Location
    lat: float = EventAttr(['latitude'], float, required=True)
    lng: float = EventAttr(['longitude'], float, required=True)

    # Gym Info
    team_id: int = EventAttr(['team_id', 'team'], int, required=True)

    gym_name: str = EventAttr(['name'], str)
    gym_description: str = EventAttr(['description'], str)
    gym_image: str = EventAttr(['url'], str)

    open_slots: int = EventAttr(['slots_available'], int)

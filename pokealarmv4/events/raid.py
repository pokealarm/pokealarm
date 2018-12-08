"""
pokealarmv4.events.raid
~~~~~~~~~~~~~~~~

This module contains classes for managing changes to a Raid ingame.
"""

# Standard Library Imports
from datetime import datetime
# 3rd Party Imports
# Local Imports
from ._base import Event, EventAttr


class Raid(Event):
    """
    Object representation of an ingame Raid.
    """

    # Identification
    gym_id = EventAttr(['gym_id', 'id'], str, required=True)

    # Location
    lat: float = EventAttr(['latitude'], float)
    lng: float = EventAttr(['longitude'], float)

    gym_name: str = EventAttr(['name'], str)
    gym_description: str = EventAttr(['description'], str)
    gym_image: str = EventAttr(['url'], str)

    team_id: int = EventAttr(['team_id', 'team'], int)
    sponsor_id: int = EventAttr(['sponsor'], int)
    park: str = EventAttr(['park'], str)

    # Time Remaining
    raid_end: datetime = EventAttr(
        ['end', 'raid_end'], datetime.utcfromtimestamp, required=True)

    @property
    def time_left(self) -> float:
        return (self.raid_end - datetime.utcnow()).total_seconds()

    # Monster Info
    raid_lvl: int = EventAttr(['level'], int, required=True)
    monster_id: int = EventAttr(['pokemon_id'], int, required=True)
    cp: int = EventAttr(['cp'], int, required=True)

    form_id: int = EventAttr(['form'], int, default=0)
    costume_id: int = EventAttr(['costume'], int, default=0)

    quick_id: int = EventAttr(['move_1'], int)
    charge_id: int = EventAttr(['move_2'], int)

    # Weather Info
    weather_id: int = EventAttr(['weather'], int)

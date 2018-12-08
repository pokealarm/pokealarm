"""
pokealarmv4.events.monster
~~~~~~~~~~~~~~~~

This module contains classes for managing catchable monsters that spawn ingame.
"""
# Standard Library Imports
from datetime import datetime
from typing import Optional
# 3rd Party Imports
# Local Imports
from ._base import Event, EventAttr


class Monster(Event):
    """
    Object representation of a catchable monster being observed.
    """

    # Identification
    enc_id: str = EventAttr(['encounter_id'], str, required=True)
    monster_id: int = EventAttr(['pokemon_id'], int, required=True)

    # Location
    lat: Optional[float] = EventAttr(['latitude'], float)
    lng: Optional[float] = EventAttr(['longitude'], float)

    # Time Left
    disappear_time: datetime = EventAttr(
        ['disappear_time'], datetime.utcfromtimestamp, required=True)

    @property
    def time_left(self) -> float:
        return (self.disappear_time - datetime.utcnow()).total_seconds()

    # Spawn data
    spawn_start: Optional[int] = EventAttr(['spawn_start'], int)
    spawn_end: Optional[int] = EventAttr(['spawn_end'], int)
    spawn_verified: bool = EventAttr(
        ['verified'], bool, default=False)

    # Encounter Stats
    mon_lvl: Optional[int] = EventAttr(['pokemon_level'], int)
    cp: Optional[int] = EventAttr(['cp'], int)

    atk_iv: Optional[int] = EventAttr(['individual_attack'], int)
    def_iv: Optional[int] = EventAttr(['individual_defense'], int)
    sta_iv: Optional[int] = EventAttr(['individual_stamina'], int)

    @property
    def iv(self) -> Optional[float]:
        if None in [self.atk_iv, self.def_iv, self.sta_iv]:
            return None
        return 100 * (self.atk_iv + self.def_iv + self.sta_iv) / 45.0

    # Moves
    quick_id: Optional[int] = EventAttr(['move_1'], int)
    charge_id: Optional[int] = EventAttr(['move_2'], int)

    atk_grade: Optional[str] = EventAttr(['atk_grade'], str)
    def_grade: Optional[str] = EventAttr(['def_grade'], str)

    # Cosmetic
    gender_id: Optional[int] = EventAttr(['gender'], int)
    height: Optional[float] = EventAttr(['height'], float)
    weight: Optional[float] = EventAttr(['weight'], float)

    @property
    def size_id(self) -> int:
        return 0  # TODO: Actually implement this

    form_id: Optional[int] = EventAttr(['form'], int)
    costume_id: Optional[int] = EventAttr(['costume'], int)
    rarity_id: Optional[int] = EventAttr(['rarity'], int)

    weather_id: Optional[int] = EventAttr(['weather'], int)
    boosted_weather_id: int = EventAttr(
        ['boosted_weather', 'weather_boosted_condition'], int, default=0)

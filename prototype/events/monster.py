# -*- coding: utf-8 -*-

"""
pokealarm.events.monster
~~~~~~~~~~~~~~~~

This module contains classes for managing catchable monsters that spawn ingame.
"""

# Standard Library Imports
from datetime import datetime
# 3rd Party Imports
# Local Imports
from prototype.events import Event, _EventAttr


class Monster(Event):
    """
    Object representation of a catchable monster spawning.
    """

    # Location
    lat = _EventAttr(['latitude'], float)  # type: float
    lng = _EventAttr(['longitude'], float)  # type: float
    # Completed by Manager
    distance = None  # type: float
    direction = None  # type: str

    # Identification
    enc_id = _EventAttr(['encounter_id'], str, required=True)  # type: str
    monster_id = _EventAttr(['pokemon_id'], int, required=True)  # type: int

    # Time Left
    disappear_time = _EventAttr(
        ['disappear_time'], datetime.utcfromtimestamp, True)  # type: datetime

    @property
    def time_left(self):
        # type: () -> float
        return (self.disappear_time - datetime.utcnow()).total_seconds()

    # Spawn data
    spawn_start = _EventAttr(['spawn_start'], int)  # type: int
    spawn_end = _EventAttr(['spawn_end'], int)  # type: int
    spawn_verified = _EventAttr(
        ['verified'], bool, default=False)  # type: bool

    # Encounter Stats
    mon_lvl = _EventAttr(['pokemon_level'], int)  # type: int
    cp = _EventAttr(['cp'], int)  # type: int

    atk_iv = _EventAttr(['individual_attack'], int)  # type: int
    def_iv = _EventAttr(['individual_defense'], int)  # type: int
    sta_iv = _EventAttr(['individual_stamina'], int)  # type: int

    @property
    def iv(self):
        # type: () -> float
        if None in [self.atk_iv, self.def_iv, self.sta_iv]:
            return None
        return 100 * (self.atk_iv + self.def_iv + self.sta_iv) / 45.0

    # Moves
    quick_id = _EventAttr(['move_1'], int)  # type: int
    charge_id = _EventAttr(['move_2'], int)  # type: int

    atk_grade = _EventAttr(['atk_grade'], str)  # type: str
    def_grade = _EventAttr(['def_grade'], str)  # type: str

    # Cosmetic
    gender_id = _EventAttr(['gender'], int)  # type: int
    height = _EventAttr(['height'], float)  # type: float
    weight = _EventAttr(['weight'], float)  # type: float

    @property
    def size_id(self):
        # {} -> int
        return 0  # TODO: Actually implement this

    form_id = _EventAttr(['form'], int)  # type: int
    costume_id = _EventAttr(['costume'], int)  # type: int
    rarity_id = _EventAttr(['rarity'], int)  # type: int

    weather_id = _EventAttr(['weather'], int)  # type: int
    boosted_weather_id = _EventAttr(
        ['boosted_weather', 'weather_boosted_condition'],
        int, default=0)  # type: int

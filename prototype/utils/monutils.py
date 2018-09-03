# -*- coding: utf-8 -*-

"""
pokealarm.utils.monutils
~~~~~~~~~~~~~~~~

This module contains utility functions for data related to Monsters
"""

# Standard Library Imports
from __future__ import absolute_import, unicode_literals
# 3rd Party Imports
# Local Imports
from ._data import mon_stats, move_stats, cp_mult, weather_boosts


def get_atk_stat(mon_id):
    """ Returns the attack stat for a monster species. """
    # (int) -> int
    return mon_stats['attack'].get(mon_id)


def get_def_stat(mon_id):
    """ Returns the defense stat for a monster species. """
    # (int) -> int
    return mon_stats['defense'].get(mon_id)


def get_sta_stat(mon_id):
    """ Returns the stamina stat for a monster species. """
    # (int) -> int
    return mon_stats['stamina'].get(mon_id)


def get_types(mon_id):
    """ Returns a tuple containing the type ids for the monsters. """
    # (int) -> tuple[int]
    t1, t2 = mon_stats['type1'].get(mon_id), mon_stats['type2'].get(mon_id)
    # Only return  types if they exist
    return (t1, t2) if t2 else ((t1,) if t1 else None)


def is_legendary(mon_id):
    """ Returns true if the monster is a legendary. """
    # (int) -> bool
    return mon_stats['legendary'].get(mon_id)


def get_generation(mon_id):
    """ Returns the generation the monster belongs too. """
    # (int) -> int
    return mon_stats['generation'].get(mon_id)


def get_height(mon_id):
    """ Returns the height stat for a monster. """
    # (int) -> float
    return mon_stats['height'].get(mon_id)


def get_weight(mon_id):
    """ Returns the weight stat for a monster. """
    # (int) -> float
    return mon_stats['weight'].get(mon_id)


def get_move_type(move_id):
    """ Returns the type of damage a move inflicts. """
    # (int) -> int
    return move_stats['type'].get(move_id)


def get_move_damage(move_id):
    """ Returns the amount of damage a move inflicts. """
    # (int) -> int
    return move_stats['damage'].get(move_id)


def get_move_dps(move_id):
    """ Returns the average dps of a move. """
    # (int) -> float
    return move_stats['dps'].get(move_id)


def get_move_duration(move_id):
    """ Returns the time a move takes to execute. """
    # (int) -> int
    return move_stats['duration'].get(move_id)


def get_move_energy(move_id):
    """ Returns the energy a move generates. """
    # (int) -> int
    return move_stats['energy'].get(move_id)


def get_weather_boosted_types(weather_id):
    """ Returns the types boosted by a supplied weather type. """
    # (int) -> list[int]
    return weather_boosts.get(weather_id)


def get_cp_multiplier(lvl):
    """ Returns the cp multiplier for a given level. """
    # (float) -> int
    return cp_mult.get(lvl)

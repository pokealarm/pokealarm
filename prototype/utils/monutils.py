# -*- coding: utf-8 -*-

"""
pokealarm.utils.monutils
~~~~~~~~~~~~~~~~

This module contains utility functions for data related to Monsters
"""

# Standard Library Imports
# 3rd Party Imports
# Local Imports
from _data import mon_stats


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

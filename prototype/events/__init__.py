# -*- coding: utf-8 -*-

"""
pokealarm.events
~~~~~~~~~~~~~~~~

This module contains the objects for creating and representing different events
of importance that can occur.
"""

# Standard Library Imports
from __future__ import absolute_import
# 3rd Party Imports
# Local Imports
from .monster import Monster
from .stop import Stop
from .gym import Gym
from .egg import Egg
from .raid import Raid
from .weather import Weather
from .quest import Quest

TYPES = [Monster, Stop, Gym, Egg, Raid, Weather, Quest]

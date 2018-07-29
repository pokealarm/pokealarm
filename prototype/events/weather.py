# -*- coding: utf-8 -*-

"""
pokealarm.events.egg
~~~~~~~~~~~~~~~~

This module contains classes for managing changes to Weather ingame.
"""

# Standard Library Imports
# 3rd Party Imports
# Local Imports
from _base import Event, EventAttr


class Weather(Event):
    """
    Object representation of an changes to a s2_cell's weather.
    """

    # Location
    lat = EventAttr(['latitude'], float)  # type: float
    lng = EventAttr(['longitude'], float)  # type: float
    # Completed by Manager
    distance = None  # type: float
    direction = None  # type: str

    # Identification
    s2_cell_id = EventAttr(['s2_cell_id'], str, required=True)  # type: str

    # Weather
    weather_id = EventAttr(  # type: int
        ['condition', 'gameplay_weather'], int)
    severity_id = EventAttr(['alert_severity', 'severity'], int)  # type: int
    day_or_night_id = EventAttr(['day', 'world_time'], int)  # type: int

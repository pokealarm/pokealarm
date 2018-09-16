# -*- coding: utf-8 -*-

"""
pokealarm.events.quest
~~~~~~~~~~~~~~~~

This module contains classes for managing changes to quests.
"""

# Standard Library Imports
from datetime import datetime
# 3rd Party Imports
# Local Imports
from _base import Event, EventAttr


class Quest(Event):
    """
    Object representation of a change to a quest.
    """

    # Location
    lat = EventAttr(['latitude'], float)  # type: float
    lng = EventAttr(['longitude'], float)  # type: float
    # Completed by Manager
    distance = None  # type: float
    direction = None  # type: str

    # Identification
    stop_id = EventAttr(['pokestop_id'], str, required=True)  # type: str
    type = EventAttr(['type'], int, default=0)  # type: int

    # Details
    quest = EventAttr(['quest'], str, required=True)  # type: str
    reward = EventAttr(['reward'], str, required=True)  # type: str

    @property
    def expiry(self):
        # type: () -> str
        return datetime.now().strftime("%d/%m/%Y 23:59")

    stop_image = EventAttr(['stop_image'], str)
    stop_name = EventAttr(['stop_name'], str)

# -*- coding: utf-8 -*-

"""
pokealarm.events.quest
~~~~~~~~~~~~~~~~

This module contains classes for managing changes to quests.
"""

# Standard Library Imports
from datetime import datetime, date, time
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
    # TODO: distance and direction by manager
    # Completed by Manager
    distance = None  # type: float
    direction = None  # type: str

    # Identification
    stop_id = EventAttr(['pokestop_id'], str, required=True)  # type: str
    reward_type = EventAttr(['type'], int, default=0)  # type: int

    # Details
    quest = EventAttr(['quest'], str, required=True)  # type: str
    reward = EventAttr(['reward'], str, required=True)  # type: str
    expire_time = EventAttr(
        ['expire_time'], datetime.utcfromtimestamp,
        default=(datetime.combine(date.today(), time(23, 59))
                 - datetime(1970, 1, 1)).total_seconds())
    # type: float

    stop_image = EventAttr(['pokestop_url', 'url'], str)  # type: str
    stop_name = EventAttr(['pokestop_name', 'name'], str)  # type: str

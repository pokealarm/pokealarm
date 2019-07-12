"""
pokealarmv4.controllers._base
~~~~~~~~~~~~~~~~

This module contains base classes and helpers for controllers.
"""
# Standard Library Imports
from abc import ABC, abstractmethod
from typing import List
# 3rd Party Imports
# Local Imports


class EventController(ABC):

    @abstractmethod
    async def update(self, id_) -> List[str]:
        pass

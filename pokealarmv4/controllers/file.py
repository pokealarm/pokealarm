"""
pokealarmv4.controllers.file
~~~~~~~~~~~~~~~~

This module contains controllers for maintaining access to different resources
using sqlalchemy.
"""
# Standard Library Imports
import asyncio
import pickle
from collections import defaultdict
from typing import Dict, List
from pathlib import Path
from os import PathLike
# 3rd Party Imports
import aiofiles
# Local Imports
from pokealarmv4.events import Event
from ._base import EventController


class FileController(object):

    _path: Path = None
    _contents: Dict = defaultdict(dict)
    _task: asyncio.Task = None

    async def _init(self):
        """
        Asynchronously initialize the :class:`~file.FileController`.
        :method:`_init` should be awaited before use.
        """
        try:
            # If file exists, load previous contents
            if self._path.exists():
                await self._load()
            # Start a task to periodically save contents
            self._task = asyncio.create_task(self._periodic_save())
        except PermissionError as ex:
            raise ex

    async def _load(self):
        """ Loads the contents of the controller from file. """
        async with aiofiles.open(self._path) as f:
            contents = await f.read()
        self._contents = pickle.loads(contents)

    async def _save(self):
        """ Writes the contents of the controller to file. """
        contents = pickle.dumps(self._contents)
        async with aiofiles.open(self._path) as f:
            await f.write(contents)

    async def _periodic_save(self):
        """ Saves the contents of the controller every 10 seconds. """
        while True:
            await asyncio.sleep(10)
            await self._save()


class EventFileController(EventController, FileController):

    def __init__(self, path: PathLike):
        self._path = Path(path)

    async def update(self, event: Event) -> List[str]:
        event_hist = self._contents[event.id]
        old = event_hist.get(event.id)
        event_hist[event.id] = event
        return old

# Standard Library Imports
import os
# 3rd Party Imports
import logging
import pickle
import portalocker
import traceback
# Local Imports
from ..Utils import get_path
from . import Cache

log = logging.getLogger('FileCache')


class FileCache(Cache):

    def __init__(self, name):
        """ Initialize a new cache object, retrieving and previously saved results if possible. """
        super(FileCache, self).__init__()
        self._name = name
        self._file = get_path(os.path.join("cache", "{}.cache".format(name)))

        log.debug("Checking for previous cache at {}".format(self._file))
        if os.path.isfile(self._file):
            self._load()
        else:
            with portalocker.Lock(self._file, mode="wb+") as f:
                pickle.dump({}, f, protocol=pickle.HIGHEST_PROTOCOL)

    def _load(self):
        with portalocker.Lock(self._file, mode="rb") as f:
            data = pickle.load(f)
            self._pokemon_hist = data.get('pokemon_hist', {})
            self._pokestop_hist = data.get('pokestop_hist', {})
            self._gym_team = data.get('gym_team', {})
            self._gym_info = data.get('gym_info', {})
            self._egg_hist = data.get('egg_hist', {})
            self._raid_hist = data.get('raid_hist', {})
            log.debug("LOADED: \n {}".format(data))

    def _save(self):
        """ Export the data to a more permanent location. """
        log.debug("Writing cache to file...")
        data = {
            'pokemon_hist': self._pokemon_hist,
            'pokestop_hist': self._pokestop_hist,
            'gym_team': self._gym_team,
            'gym_info': self._gym_info,
            'egg_hist': self._egg_hist,
            'raid_hist': self._raid_hist
        }
        log.debug(self._pokestop_hist)
        log.debug("SAVED: {}".format(data))
        try:
            with portalocker.Lock(self._file, timeout=5, mode="wb+") as f:
                pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            log.error("Encountered error while saving cache: {}: {}".format(type(e).__name__, e))
            log.debug("Stack trace: \n {}".format(traceback.format_exc()))

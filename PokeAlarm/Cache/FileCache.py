# Standard Library Imports
import os
# 3rd Party Imports
import pickle
import portalocker
import traceback
# Local Imports
from ..Utils import get_path
from . import Cache


class FileCache(Cache):

    def __init__(self, mgr):
        """ Initializes a new cache object for storing data between events. """
        super(FileCache, self).__init__(mgr)
        self._name = mgr.get_name()
        self._file = get_path(
            os.path.join("cache", "{}.cache".format(self._name)))

        self._log.debug("Checking for previous cache at {}".format(self._file))
        cache_folder = get_path("cache")
        if not os.path.exists(cache_folder):
            os.makedirs(cache_folder)
        if os.path.isfile(self._file):
            self._load()
        else:
            self._save()

    def _load(self):
        try:
            with portalocker.Lock(self._file, mode="rb") as f:
                data = pickle.load(f)
                self._mon_hist = data.get('mon_hist', {})
                self._stop_hist = data.get('stop_hist', {})
                self._egg_hist = data.get('egg_hist', {})
                self._raid_hist = data.get('raid_hist', {})
                self._gym_team = data.get('gym_team', {})
                self._gym_name = data.get('gym_name', {})
                self._gym_desc = data.get('gym_desc', {})
                self._gym_image = data.get('gym_image', {})
                self._cell_weather_id = data.get('cell_weather_id', {})
                self._severity_id = data.get('severity_id', {})
                self._day_or_night_id = data.get('day_or_night_id', {})

                self._log.debug("Cache loaded successfully.")
        except Exception as e:
            self._log.error(
                "There was an error attempting to load the cache. "
                "The old cache will be overwritten.")
            self._log.error("{}: {}".format(type(e).__name__, e))

    def _save(self):
        """ Export the data to a more permanent location. """
        self._log.debug("Writing cache to file...")
        data = {
            'mon_hist': self._mon_hist,
            'stop_hist': self._stop_hist,
            'egg_hist': self._egg_hist,
            'raid_hist': self._raid_hist,
            'gym_team': self._gym_team,
            'gym_name': self._gym_name,
            'gym_desc': self._gym_desc,
            'gym_image': self._gym_image,
            'cell_weather_id': self._cell_weather_id,
            'severity_id': self._severity_id,
            'day_or_night_id': self._day_or_night_id
        }
        try:
            # Write to temporary file and then rename
            temp = self._file + ".new"
            with portalocker.Lock(self._file + ".lock", timeout=5, mode="wb+"):
                with portalocker.Lock(temp, timeout=5, mode="wb+") as f:
                    pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
                if os.path.exists(self._file):
                    os.remove(self._file)  # Required for Windows
                os.rename(temp, self._file)
            self._log.debug("Cache saved successfully.")
        except Exception as e:
            self._log.error("Encountered error while saving cache: "
                            "{}: {}".format(type(e).__name__, e))
            self._log.error(
                "Stack trace: \n {}".format(traceback.format_exc()))

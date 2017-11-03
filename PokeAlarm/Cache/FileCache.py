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
        self.__name = name
        self.__file = get_path(os.path.join("cache", "{}.cache".format(name)))

        log.debug("Checking for previous cache at {}".format(self.__file))
        if os.path.isfile(self.__file):
            self.__load()
        else:
            with portalocker.Lock(self.__file, mode="w+") as f:
                pickle.dump({}, f, protocol=pickle.HIGHEST_PROTOCOL)

    def __load(self):
        with portalocker.Lock(self.__file, mode="r") as f:
            data = pickle.load(f)
            self.__pokemon_hist = data.get('pokemon_hist')
            self.__pokestop_hist = data.get('pokestop_hist')
            self.__gym_team = data.get('gym_team')
            self.__gym_info = data.get('gym_info')
            self.__egg_hist = data.get('egg_hist')
            self.__raid_hist = data.get('raid_hist')

    def save(self):
        """ Export the data to a more permanent location. """
        data = {
            'pokemon_hist': self.__pokemon_hist,
            'pokestop_hist': self.__pokestop_hist,
            'gym_team': self.__gym_team,
            'gym_info': self.__gym_info,
            'egg_hist': self.__egg_hist,
            'raid_hist': self.__raid_hist
        }
        try:
            with portalocker.Lock(self.__file, timeout=5, mode="w+") as f:
                pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            log.error("Encountered error while saving cache: {}: {}".format(type(e).__name__, e))
            log.debug("Stack trace: \n {}".format(traceback.format_exc()))

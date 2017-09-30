import pickle
import os.path
import errno
import logging

log = logging.getLogger('Cache')


# Cache helper object
# Caches the reverse geocode lookup of coordinates to addresses
# and the gym details
class Cache(object):
    def __init__(self, name, use_adr_cache, use_gym_cache):
        self.adr_cache = {}
        self.gym_cache = {}
        self.__name = name
        self.__use_adr_cache = use_adr_cache
        self.__use_gym_cache = use_gym_cache
        self.__pkl_file_adr = '.pickles/cached_{}_adr.pkl'.format(name)
        self.__pkl_file_gym = '.pickles/cached_{}_gym.pkl'.format(name)

    # load the cache
    @staticmethod
    def load_pickle(file_name):
        try:
            with open(file_name, 'r+') as pickle_file:
                cache = pickle.load(pickle_file)
                log.info("Loaded cache with {} entries".format(len(cache)))

            return cache
        except (OSError, IOError):
            log.warn("Unable to load the pickle {}, starting fresh".format(file_name))
            return {}

    # Save a cache to pickle file for easy reuse.
    @staticmethod
    def save_pickle(cache, file_name):
        log.info("Saving cache with {} entries".format(len(cache)))
        with open(file_name, 'w+') as pickle_file:
            pickle.dump(cache, pickle_file)

    # Load the cache from pickle files
    def load(self):
        if self.__use_adr_cache:
            self.adr_cache = self.load_pickle(self.__pkl_file_adr)

        if self.__use_gym_cache:
            self.gym_cache = self.load_pickle(self.__pkl_file_gym)

    # Save the cache into pickle files.
    def save(self):
        if (self.__use_adr_cache or self.__use_gym_cache) and not os.path.exists('.pickles'):
            try:
                os.makedirs('.pickles')
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        if self.__use_adr_cache:
            self.save_pickle(self.adr_cache,self.__pkl_file_adr)

        if self.__use_gym_cache:
            self.save_pickle(self.gym_cache,self.__pkl_file_gym)

# Standard Library Imports
import logging
from datetime import datetime
# 3rd Party Imports
# Local Imports
from ..Utils import get_image_url

log = logging.getLogger('Cache')


class Cache(object):
    """ Basic object for caching information.

    This object caches and manages information in Memory. Information will be lost between run times if save has not
    been implemented correctly.
    """

    __default_gym_info = {
        "name": "unknown",
        "description": "unknown",
        "url":  get_image_url('icons/gym_0.png')
    }

    def __init__(self):
        """ Initialize a new cache object, retrieving and previously saved results if possible. """
        self.__pokemon_hist = {}
        self.__pokestop_hist = {}
        self.__gym_team = {}
        self.__gym_info = {}
        self.__egg_hist = {}
        self.__raid_hist = {}

    def get_pokemon_expiration(self, pkmn_id):
        """ Get the datetime that the pokemon expires."""
        return self.__pokemon_hist.get(pkmn_id)

    def update_pokemon_expiration(self, pkmn_id, expiration):
        """ Updates the datetime that the pokemon expires. """
        self.__pokemon_hist[pkmn_id] = expiration

    def get_pokestop_expiration(self, stop_id):
        """ Returns the datetime that the pokemon expires. """
        return self.__pokestop_hist.get(stop_id)

    def update_pokestop_expiration(self, stop_id, expiration):
        """ Updates the datetime that the pokestop expires. """
        self.__pokestop_hist[stop_id] = expiration

    def get_gym_team(self, gym_id):
        """ Get the current team that owns the gym. """
        return self.__gym_team.get(gym_id, '?')

    def update_gym_team(self, gym_id, team):
        """ Update the current team of the gym. """
        self.__gym_team[gym_id] = team

    def get_gym_info(self, gym_id):
        """ Gets the information about the gym. """
        return self.__gym_info.get(gym_id, self.__default_gym_info)

    def update_gym_info(self, gym_id, name, desc, url):
        """ Updates the information about the gym. """
        if name != 'unknown':  # Don't update if the gym info is missing
            self.__gym_info[gym_id] = {"name": name, "description": desc, "url": url}

    def get_egg_expiration(self, gym_id):
        """ Updates the datetime that the egg expires. """
        return self.__egg_hist.get(gym_id)

    def update_egg_expiration(self, gym_id, expiration):
        """ Updates the datetime that the egg expires. """
        self.__egg_hist[gym_id] = expiration

    def get_raid_expiration(self, gym_id):
        """ Updates the datetime that the raid_ expires. """
        self.__raid_hist.get(gym_id)

    def update_raid_expiration(self, gym_id, expiration):
        """ Updates the datetime that the egg expires. """
        self.__raid_hist[gym_id] = expiration

    def save(self):
        """ Export the data to a more permanent location. """
        self.__clean_hist()
        log.debug("Cache cleaned!")

    def __clean_hist(self):
        """ Clean expired objects to free up memory """
        for dict_ in (self.__pokemon_hist, self.__pokestop_hist, self.__egg_hist, self.__raid_hist):
            old = []
            for id_ in dict_:  # Gather old events
                if dict_[id_] < datetime.utcnow():
                    old.append(id_)
            for id_ in old:  # Remove gathered events
                del dict_[id_]

# Standard Library Imports
# 3rd Party Imports
# Local Imports


class Cache(object):
    """ Basic interface for caching information.

    This interface outlines the abstract methods needed for the fetching, retrieving, and storing of information that
    would otherwise be lost between runtimes.
    """

    def __init__(self):
        """ Initialize a new cache object, retrieving and previously saved results if possible. """
        raise NotImplementedError("This is an abstract method.")

    def get_pokemon_expiration(self, id):
        """ Get the datetime that the pokemon expires."""
        raise NotImplementedError("This is an abstract method.")

    def update_pokemon_expiration(self, data):
        """ Updates the datetime that the pokemon expires. """
        raise NotImplementedError("This is an abstract method.")

    def get_pokestop_expiration(self, id):
        """ Returns the datetime that the pokemon expires. """
        raise NotImplementedError("This is an abstract method.")

    def get_pokestop_expiration(self, data):
        """ Updates the datetime that the pokestop expires. """
        raise NotImplementedError("This is an abstract method.")

    def get_gym_info(self, id):
        """ Gets the information about the gym. """
        raise NotImplementedError("This is an abstract method.")

    def update_gym_info(self, data):
        """ Updates the information about the gym. """
        raise NotImplementedError("This is an abstract method.")

    def get_egg_expiration(self, id):
        """ Updates the datetime that the egg expires. """
        raise NotImplementedError("This is an abstract method.")

    def update_egg_expiration(self, data):
        """ Updates the datetime that the egg expires. """
        raise NotImplementedError("This is an abstract method.")

    def get_raid_information(self, id):
        """ Updates the datetime that the raid expires. """
        raise NotImplementedError("This is an abstract method.")

    def update_raid_information(self, data):
        """ Updates the datetime that the egg expires. """
        raise NotImplementedError("This is an abstract method.")

    def save(self):
        """ Export the data to a more permanent location. """
        raise NotImplementedError("This is an abstract method.")
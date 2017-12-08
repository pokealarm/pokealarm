# Global variables used by all functions
config = {}


class Unknown:
    """ Enum for unknown DTS. """
    TINY = '?'
    SMALL = '???'
    REGULAR = 'unknown'
    EMPTY = ''

    __unknown_set = {TINY, SMALL, REGULAR}

    @classmethod
    def is_not(cls, *args):
        """ Returns false if any given arguments are unknown, else true """
        for arg in args:
            if arg in cls.__unknown_set:
                return False
        return True

    @classmethod
    def or_empty(cls, val, default=''):
        """ Returns an default if unknown, else the original value. """
        return cls.EMPTY if val in cls.__unknown_set else default

from Cache import Cache
from FileCache import FileCache

cache_options = ["mem", "file"]


def cache_factory(kind, name):
    if kind == cache_options[0]:
        return Cache()
    elif kind == cache_options[1]:
        return FileCache(name)
    else:
        raise ValueError("%s is not a valid cache type!".format(kind))

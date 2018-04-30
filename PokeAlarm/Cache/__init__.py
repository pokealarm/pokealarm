from Cache import Cache
from FileCache import FileCache

cache_options = ["mem", "file"]


def cache_factory(mgr, kind):
    if kind == cache_options[0]:
        return Cache(mgr)
    elif kind == cache_options[1]:
        return FileCache(mgr)
    else:
        raise ValueError("%s is not a valid cache type!".format(kind))

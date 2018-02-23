# Standard Library Imports
# 3rd Party Imports
from gevent.lock import Semaphore
# Local Imports


def parse_bool(value):
    try:
        b = str(value).lower()
        if b in {'t', 'true', 'y', 'yes'}:
            return True
        if b in {'f', 'false', 'n', 'no'}:
            return False
    except Exception:
        pass  # Skip below
    raise ValueError('Not a valid boolean')


def synchronize_with(lock=None):
    """ Synchronization decorator. """

    if lock is None:
        lock = Semaphore()

    def synchronize(func):

        def locked_func(*args, **kwargs):
            lock.acquire(timeout=60)
            try:
                return func(*args, **kwargs)
            finally:
                lock.release()

        return locked_func

    return synchronize

# Standard Library Imports
import logging
import logging.handlers
import os
import sys
# 3rd Party Imports
# Local Imports
from PokeAlarm.Utils import get_path

FORMAT = '%(asctime)s [%(levelname)5.5s]' \
         '[%(parent)10.10s][%(child)10.10s] %(message)s'

FORMATTER = logging.Formatter(FORMAT)


class LevelFilter(logging.Filter):
    """ Filter to restrict log records based on level."""

    def __init__(self, level):
        super(LevelFilter, self).__init__()
        self.level = level

    def filter(self, record):
        return record.levelno < self.level


class ContextFilter(logging.Filter):
    """ Filter to apply extra context based on logger name. """
    def filter(self, record):
        levels = record.name.split('.')

        if len(levels) > 1:
            record.parent = levels[-2]
            record.child = levels[-1]
        else:
            record.parent = 'external'
            record.child = levels[0]

        return True


def setup_std_handler(logger):
    """ Creates a handler to direct output to stdout and stderr. """
    # setup stdout
    stdout = logging.StreamHandler(sys.stdout)
    stdout.setFormatter(FORMATTER)
    stdout.addFilter(ContextFilter())
    stdout.addFilter(LevelFilter(logging.WARNING))
    logger.addHandler(stdout)
    # setup stderr
    stderr = logging.StreamHandler(sys.stderr)
    stderr.setFormatter(FORMATTER)
    stderr.addFilter(ContextFilter())
    stderr.setLevel(logging.WARNING)
    # Attach it to the logger
    logger.addHandler(stderr)


def setup_file_handler(logger, path, max_size=100, backup_ct=5):
    """ Returns a rotating file handler. """
    # Confirm that the path  exists
    path = get_path(path)
    folder = os.path.dirname(path)
    if not os.path.exists(folder):
        raise IOError("Unable to create file logger "
                      "- path '{}' doesn't exist".format(folder))
    # Create the handler
    handler = logging.handlers.RotatingFileHandler(
        filename=path, maxBytes=max_size * (10**6), backupCount=backup_ct)
    handler.setFormatter(FORMATTER)
    handler.addFilter(ContextFilter())
    # Attach it to the logger
    logger.addHandler(handler)

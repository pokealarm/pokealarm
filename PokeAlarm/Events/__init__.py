import logging
import traceback

from Event import Event  # noqa F401
from Monster import Monster
from Stop import Stop
from Gym import Gym
from Egg import Egg
from Raid import Raid

log = logging.getLogger('Events')


def event_factory(self, data):
    """ Creates and returns the appropriate Event from the given data. """
    try:
        kind = data['type']
        message = data['message']
        if kind == 'pokemon':
            return Monster(message)
        elif kind == 'pokestop':
            return Stop(message)
        elif kind == 'gym' or kind == 'gym_details':
            return Gym(message)
        elif kind == 'raid' and message.get('pkmn_id', 0) == 0:
            return Egg(message)
        elif kind == 'raid' and message.get('pkmn_id', 0) != 0:
            return Raid(message)
        elif kind in ['captcha', 'scheduler']:
            log.debug(
                "{} data ignored - unsupported webhook type.".format(kind))
        else:
            raise ValueError("Webhook kind was not an expected value.")
    except Exception as e:
        log.error("Encountered error while converting webhook data"
                  + "({}: {})".format(type(e).__name__, e))
        log.debug("Stack trace: \n {}".format(traceback.format_exec()))

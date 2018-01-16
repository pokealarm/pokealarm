import logging
import traceback

from BaseEvent import BaseEvent  # noqa F401
from MonEvent import MonEvent
from StopEvent import StopEvent
from GymEvent import GymEvent
from EggEvent import EggEvent
from RaidEvent import RaidEvent
from WeatherEvent import WeatherEvent

log = logging.getLogger('Events')


def event_factory(data):
    """ Creates and returns the appropriate Event from the given data. """
    try:
        kind = data['type']
        message = data['message']
        if kind == 'pokemon':
            return MonEvent(message)
        elif kind == 'pokestop':
            return StopEvent(message)
        elif kind == 'gym' or kind == 'gym_details':
            return GymEvent(message)
        elif kind == 'raid' and not message.get('pokemon_id'):
            # RM sends None, M sends 0 for eggs
            return EggEvent(message)
        elif kind == 'raid' and message.get('pokemon_id'):
            # RM/M send Monster ID in raids
            return RaidEvent(message)
        elif kind == 'weather':
            return WeatherEvent(message)
        elif kind in ['captcha', 'scheduler']:
            log.debug(
                "{} data ignored - unsupported webhook type.".format(kind))
        else:
            raise ValueError("Webhook kind was not an expected value.")
    except Exception as e:
        log.error("Encountered error while converting webhook data"
                  + "({}: {})".format(type(e).__name__, e))
        log.debug("Stack trace: \n {}".format(traceback.format_exc()))

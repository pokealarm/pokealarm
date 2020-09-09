try:
    from twilio.rest import Client  # noqa F401
except ImportError:
    from PokeAlarm.Utils import pip_install

    pip_install('twilio', '6.45.1')

from .TwilioAlarm import TwilioAlarm  # noqa F401

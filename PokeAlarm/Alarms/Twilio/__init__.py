from TwilioAlarm import TwilioAlarm # noqa F401

try:
    from twilio.rest import TwilioRestClient  # noqa F401
except ImportError:
    from PokeAlarm.Utils import pip_install

    pip_install('twilio', '5.4.0')

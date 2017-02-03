try:
    from twilio.rest import TwilioRestClient
except ImportError:
    from ..Utils import pip_install

    pip_install('twilio', '5.4.0')

from TwilioAlarm import TwilioAlarm

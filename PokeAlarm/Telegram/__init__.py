try:
    import telepot
except ImportError:
    from ..Utils import pip_install

    pip_install('telepot', '8.3')

from TelegramAlarm import TelegramAlarm

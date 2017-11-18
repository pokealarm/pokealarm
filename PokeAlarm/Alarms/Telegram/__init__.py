try:
    import telepot
except ImportError:
    from PokeAlarm.Utils import pip_install

    pip_install('telepot', '8.3')

from TelegramAlarm import TelegramAlarm

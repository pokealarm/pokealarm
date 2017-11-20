from TelegramAlarm import TelegramAlarm  # noqa F401

try:
    import telepot  # noqa F401
except ImportError:
    from PokeAlarm.Utils import pip_install

    pip_install('telepot', '8.3')

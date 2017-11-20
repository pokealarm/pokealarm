from DiscordAlarm import DiscordAlarm  # noqa F401

try:
    import requests  # noqa F401
except ImportError:
    from PokeAlarm.Utils import pip_install

    pip_install('requests')

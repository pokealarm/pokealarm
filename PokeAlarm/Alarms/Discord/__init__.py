try:
    import requests
except ImportError:
    from PokeAlarm.Utils import pip_install

    pip_install('requests')

from DiscordAlarm import DiscordAlarm

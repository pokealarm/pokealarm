try:
    import requests
except ImportError:
    from ..Utils import pip_install

    pip_install('requests')

from DiscordAlarm import DiscordAlarm

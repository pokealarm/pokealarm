try:
    import twitter
except ImportError:
    from PokeAlarm.Utils import pip_install

    pip_install('twitter', '1.17.1')

from TwitterAlarm import TwitterAlarm

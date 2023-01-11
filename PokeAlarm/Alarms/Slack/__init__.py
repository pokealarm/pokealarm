try:
    import slack  # noqa F401
except ImportError:
    from PokeAlarm.Utils import pip_install

    pip_install("slackclient", "2.9.2")

from .SlackAlarm import SlackAlarm  # noqa 401

try:
    import slacker
except ImportError:
    from ..Utils import pip_install

    pip_install('slacker', '0.9.24')

from SlackAlarm import SlackAlarm

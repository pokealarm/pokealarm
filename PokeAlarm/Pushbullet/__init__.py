try:
    import pushbullet
except ImportError:
    from ..Utils import pip_install

    pip_install('pushbullet.py', '0.10.0')

from PushBulletAlarm import PushbulletAlarm

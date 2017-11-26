try:
    import pushbullet  # noqa F401
except ImportError:
    from PokeAlarm.Utils import pip_install

    pip_install('pushbullet.py', '0.10.0')

from PushBulletAlarm import PushbulletAlarm  # noqa 401

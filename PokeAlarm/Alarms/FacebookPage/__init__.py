try:
    import facebook
except ImportError:
    from PokeAlarm.Utils import pip_install
    pip_install('facebook-sdk', '2.0.0')

from FacebookPageAlarm import FacebookPageAlarm

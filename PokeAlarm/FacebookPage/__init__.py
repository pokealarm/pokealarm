try:
    import facebook
except ImportError:
    from ..Utils import pip_install
    pip_install('facebook-sdk', '2.0.0')

from FacebookPageAlarm import FacebookPageAlarm

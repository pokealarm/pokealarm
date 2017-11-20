from FacebookPageAlarm import FacebookPageAlarm  # noqa 401

try:
    import facebook  # noqa F401
except ImportError:
    from PokeAlarm.Utils import pip_install

    pip_install('facebook-sdk', '2.0.0')

try:
    import slacker  # noqa F401
except ImportError:
    from PokeAlarm.Utils import pip_install

    pip_install('slacker', '0.9.24')

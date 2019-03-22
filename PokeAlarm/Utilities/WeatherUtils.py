# Standard Library Imports
from glob import glob
import json
# 3rd Party Imports
# Local Imports
from PokeAlarm.Utils import get_path


def get_severity_id(severity):
    try:
        name = str(severity).lower()
        if not hasattr(get_severity_id, 'ids'):
            get_severity_id.ids = {}
            files = glob(get_path('locales/*.json'))
            for file_ in files:
                with open(file_, 'r') as f:
                    j = json.loads(f.read())
                    j = j['severity']
                    for id_ in j:
                        nm = j[id_].lower()
                        get_severity_id.ids[nm] = int(id_)
        if name in get_severity_id.ids:
            return get_severity_id.ids[name]
        else:
            return int(name)  # try as an integer
    except ValueError:
        raise ValueError("Unable to interpret `{}` as a valid "
                         " severity name or id.".format(severity))


def get_day_or_night_id(day_or_night):
    try:
        name = str(day_or_night).lower()
        if not hasattr(get_day_or_night_id, 'ids'):
            get_day_or_night_id.ids = {}
            files = glob(get_path('locales/*.json'))
            for file_ in files:
                with open(file_, 'r') as f:
                    j = json.loads(f.read())
                    j = j['day_or_night']
                    for id_ in j:
                        nm = j[id_].lower()
                        get_day_or_night_id.ids[nm] = int(id_)
        if name in get_day_or_night_id.ids:
            return get_day_or_night_id.ids[name]
        else:
            return int(name)  # try as an integer
    except ValueError:
        raise ValueError("Unable to interpret `{}` as a valid "
                         " day or night name or id.".format(day_or_night))

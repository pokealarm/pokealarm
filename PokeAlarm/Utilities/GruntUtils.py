# Standard Library Imports
from glob import glob
import json
# 3rd Party Imports
# Local Imports
from PokeAlarm.Utils import get_path


def get_grunt_id(grunt_name):
    try:
        name = str(grunt_name).lower()
        if not hasattr(get_grunt_id, 'ids'):
            get_grunt_id.ids = {}
            files = glob(get_path('locales/*.json'))
            for file_ in files:
                with open(file_, 'r') as f:
                    j = json.loads(f.read())
                    j = j['grunt_types']
                    for id_ in j:
                        nm = j[id_].lower()
                        try:
                            if get_grunt_id.ids[nm]:
                                get_grunt_id.ids[nm].append(int(id_))
                        except KeyError:
                            get_grunt_id.ids[nm] = [int(id_)]
        if name in get_grunt_id.ids:
            return get_grunt_id.ids[name]
        else:
            return int(name)  # try as an integer
    except ValueError:
        raise ValueError("Unable to interpret `{}` as a valid "
                         " grunt name or id.".format(grunt_name))


def get_grunt_gender(grunt_id):
    try:
        if not hasattr(get_grunt_gender, 'id'):
            get_grunt_gender.genders = {}
            file_ = get_path('locales/en.json')
            with open(file_, 'r') as f:
                j = json.loads(f.read())
                j = j['grunt_genders']
                for id_ in j:
                    get_grunt_gender.genders[id_] = j[id_]
        try:
            return get_grunt_gender.genders['{:03d}'.format(grunt_id)]
        except KeyError:
            return '?'
    except ValueError:
        raise ValueError('Unable to interpret `{}` as a valid grunt id'
                         .format(grunt_id))


def get_grunt_type_id(grunt_name):
    try:
        name = str(grunt_name).lower()
        if not hasattr(get_grunt_type_id, 'types'):
            get_grunt_type_id.types = {}
            files = glob(get_path('locales/*.json'))
            for file_ in files:
                with open(file_, 'r') as f:
                    j = json.loads(f.read())
                    j = j['types']
                    for id_ in j:
                        nm = j[id_].lower()
                        get_grunt_type_id.types[nm] = int(id_)
        if name in get_grunt_type_id.types:
            return get_grunt_type_id.types[name]
        else:
            return int(name)  # try as an integer
    except ValueError:
        # Some grunt types don't match up to a monster type
        return '?'


# Returns the gender symbol of a grunt:
def get_grunt_gender_sym(gender):  # TODO - support other languages
    gender = str(gender).lower()
    if gender == '?':
        return '?'
    if gender == '1' or gender == 'male':
        return '\u2642'  # male symbol
    elif gender == '2' or gender == 'female':
        return '\u2640'  # female symbol
    elif gender == '3' or gender == 'neutral':
        return '\u26b2'  # neutral
    else:
        return '?'  # Unknown

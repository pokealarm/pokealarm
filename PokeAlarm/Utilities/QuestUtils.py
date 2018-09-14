# Standard Library Imports
from glob import glob
import json
# 3rd Party Imports
# Local Imports
from PokeAlarm.Utils import get_path


# Returns type of quest reward (e.g. monster, dust, etc.)
def get_type(type_id):
    if isinstance(type_id, int):
        try:
            if not hasattr(get_type, 'types'):
                files = glob(get_path('locales/*.json'))
                for file_ in files:
                    with open(file_, 'r') as f:
                        j = json.loads(f.read())
                        j = j['quest_types']
                        for id_ in j:
                            get_type.types[id_] = j[id_].lower()
            if type_id in get_type.types:
                return get_type.types[type_id]
            else:
                return type_id
        except ValueError:
            raise ValueError("Unable to interpret `{}` as a valid type id"
                             .format(type_id))

# Standard Library Imports
from glob import glob
import json
# 3rd Party Imports
# Local Imports
from PokeAlarm.Utils import get_path


# Returns type of quest reward (e.g. monster, dust, etc.)
def get_type(reward_type):
    try:
        name = str(reward_type).lower()
        if not hasattr(get_type, 'ids'):
            get_type.ids = {}
            files = glob(get_path('locales/*.json'))
            for file_ in files:
                with open(file_, 'r') as f:
                    j = json.loads(f.read())
                    j = j['quest_types']
                    for id_ in j:
                        nm = j[id_].lower()
                        get_type.ids[nm] = int(id_)
        if name in get_type.ids:
            return get_type.ids[name]
        else:
            return int(name)  # try as an integer
    except ValueError:
        raise ValueError("Unable to interpret `{}` as a valid "
                         " severity name or id.".format(reward_type))
    # if isinstance(type_id, int):
    #     try:
    #         if not hasattr(get_type, 'types'):
    #             get_type.types = {}
    #             files = glob(get_path('locales/*.json'))
    #             for file_ in files:
    #                 with open(file_, 'r') as f:
    #                     j = json.loads(f.read())
    #                     j = j['quest_types']
    #                     for id_ in j:
    #                         get_type.types[id_] = j[id_]
    #         if type_id in get_type.types:
    #             return get_type.types[type_id]
    #         else:
    #             return type_id
    #     except ValueError:
    #         raise ValueError("Unable to interpret `{}` as a valid type id"
    #                          .format(type_id))

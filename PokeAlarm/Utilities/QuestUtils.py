# Standard Library Imports
from glob import glob
import json
# 3rd Party Imports
# Local Imports
from PokeAlarm.Utils import get_path


# Returns type of quest reward (e.g. monster, dust, etc.)
def get_reward_type(reward_type):
    try:
        name = str(reward_type).lower()
        if not hasattr(get_reward_type, 'ids'):
            get_reward_type.ids = {}
            files = glob(get_path('locales/*.json'))
            for file_ in files:
                with open(file_, 'r') as f:
                    j = json.loads(f.read())
                    j = j['quest_types']
                    for id_ in j:
                        nm = j[id_].lower()
                        get_reward_type.ids[nm] = int(id_)
        if name in get_reward_type.ids:
            return get_reward_type.ids[name]
        else:
            return int(name)  # try as an integer
    except ValueError:
        raise ValueError("Unable to interpret `{}` as a valid "
                         " quest reward type or id.".format(reward_type))

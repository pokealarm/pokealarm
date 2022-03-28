# Standard Library Imports
import json
# 3rd Party Imports
# Local Imports
from PokeAlarm.Utils import get_path, get_type_id, Unknown


# Returns the grunt gender id
def get_grunt_gender_id(grunt_id):
    if not hasattr(get_grunt_gender_id, 'info'):
        get_grunt_gender_id.info = {}
        file_ = get_path('data/invasions.json')
        with open(file_, 'r') as f:
            j = json.load(f)
            f.close()
        for id_ in j:
            if j[id_]["grunt"] == "Male":
                get_grunt_gender_id.info[int(id_)] = 1
            elif j[id_]["grunt"] == "Female":
                get_grunt_gender_id.info[int(id_)] = 2
            else:
                get_grunt_gender_id.info[int(id_)] = 3

    return get_grunt_gender_id.info.get(grunt_id, Unknown.TINY)


# Returns the mon types used by a grunt
def get_grunt_mon_type_id(grunt_id):
    if not hasattr(get_grunt_mon_type_id, 'info'):
        get_grunt_mon_type_id.info = {}
        file_ = get_path('data/invasions.json')
        with open(file_, 'r') as f:
            j = json.load(f)
            f.close()
        for id_ in j:
            get_grunt_mon_type_id.info[int(id_)] = get_type_id(
                j[id_].get('type'))

    return get_grunt_mon_type_id.info.get(grunt_id, Unknown.TINY)


# Returns the possible mon id rewards
def get_grunt_reward_mon_id(grunt_id):
    if not hasattr(get_grunt_reward_mon_id, 'info'):
        get_grunt_reward_mon_id.info = {}
        file_ = get_path('data/invasions.json')
        with open(file_, 'r') as f:
            j = json.load(f)
            f.close()
        for id_ in j:
            get_grunt_reward_mon_id.info[int(id_)] = []
            if "pokemon" in j[id_]:
                for i in range(1, 4):
                    if j[id_]["pokemon"][str(i)]["isReward"]:
                        get_grunt_reward_mon_id.info[int(id_)].extend(
                            j[id_]["pokemon"][str(i)]["ids"])

    return get_grunt_reward_mon_id.info.get(grunt_id, [])


# Returns the possible mon id for each battle
def get_grunt_mon_battle(grunt_id, battle_num):
    if not hasattr(get_grunt_mon_battle, 'info'):
        get_grunt_mon_battle.info = {}
        file_ = get_path('data/invasions.json')
        with open(file_, 'r') as f:
            j = json.load(f)
            f.close()
        for id_ in j:
            if "pokemon" in j[id_]:
                for i in range(1, 4):
                    get_grunt_mon_battle.info[f'{id_}_{i}'] = j[id_][
                        "pokemon"][str(i)]["ids"]

    return get_grunt_mon_battle.info.get(f'{grunt_id}_{battle_num}', [])

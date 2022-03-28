# Standard Library Imports
from glob import glob
import json
# 3rd Party Imports
# Local Imports
from PokeAlarm.Utils import get_path


# Returns the id corresponding with the pokemon name
# (use all locales for flexibility)
def get_monster_id(pokemon_name):
    try:
        name = str(pokemon_name).lower()
        if not hasattr(get_monster_id, 'ids'):
            get_monster_id.ids = {}
            files = glob(get_path('locales/*.json'))
            for file_ in files:
                with open(file_, 'r') as f:
                    j = json.loads(f.read())
                    j = j['pokemon']
                    for id_ in j:
                        nm = j[id_].lower()
                        get_monster_id.ids[nm] = int(id_)
        if name in get_monster_id.ids:
            return get_monster_id.ids[name]
        else:
            return int(name)  # try as an integer
    except ValueError:
        raise ValueError("Unable to interpret `{}` as a valid "
                         " monster name or id.".format(pokemon_name))


# Returns the id corresponding with the move (use all locales for flexibility)
def get_move_id(move_name):
    try:
        name = str(move_name).lower()
        if not hasattr(get_move_id, 'ids'):
            get_move_id.ids = {}
            files = glob(get_path('locales/*.json'))
            for file_ in files:
                with open(file_, 'r') as f:
                    j = json.loads(f.read())
                    j = j['moves']
                    for id_ in j:
                        nm = j[id_].lower()
                        get_move_id.ids[nm] = int(id_)
        if name in get_move_id.ids:
            return get_move_id.ids[name]
        else:
            return int(name)  # try as an integer
    except Exception:
        raise ValueError("Unable to interpret `{}` as a valid "
                         " move name or id.".format(move_name))


# Returns the id corresponding with the move (use all locales for flexibility)
def get_size_id(size_name):
    try:
        name = str(size_name).lower()
        if not hasattr(get_size_id, 'sizes'):
            get_size_id.ids = {}
            files = glob(get_path('locales/*.json'))
            for file_ in files:
                with open(file_, 'r') as f:
                    j = json.loads(f.read())
                    j = j['sizes']
                    for id_ in j:
                        nm = j[id_].lower()
                        get_size_id.ids[nm] = int(id_)
        if name in get_size_id.ids:
            return get_size_id.ids[name]
        else:
            return int(name)  # try as an integer
    except Exception:
        raise ValueError("Unable to interpret `{}` as a valid"
                         " size name or id.".format(size_name))


# Returns the id corresponding with the type (use all locales for flexibility)
def get_type_id(type_name):
    try:
        name = str(type_name).lower()
        if not hasattr(get_type_id, 'types'):
            get_type_id.ids = {}
            files = glob(get_path('locales/*.json'))
            for file_ in files:
                with open(file_, 'r') as f:
                    j = json.loads(f.read())
                    j = j['types']
                    for id_ in j:
                        nm = j[id_].lower()
                        get_type_id.ids[nm] = int(id_)
        if name in get_type_id.ids:
            return get_type_id.ids[name]
        else:
            return int(name)  # try as an integer
    except Exception:
        raise ValueError("Unable to interpret `{}` as a valid"
                         " type name or id.".format(type_name))


# Returns the id corresponding with the rarity
def get_rarity_id(rarity_name):
    try:
        name = str(rarity_name).lower()
        if not hasattr(get_rarity_id, 'rarity'):
            get_rarity_id.ids = {}
            files = glob(get_path('locales/*.json'))
            for file_ in files:
                with open(file_, 'r') as f:
                    j = json.loads(f.read())
                    j = j['rarity']
                    for id_ in j:
                        nm = j[id_].lower()
                        get_rarity_id.ids[nm] = int(id_)
        if name in get_rarity_id.ids:
            return get_rarity_id.ids[name]
        else:
            return int(name)  # try as an integer
    except Exception:
        raise ValueError("Unable to interpret `{}` as a valid"
                         " rarity name or id.".format(rarity_name))


# Returns the gender symbol of a pokemon:
def get_pokemon_gender(gender):
    if gender == 1:
        return '\u2642'  # male symbol
    elif gender == 2:
        return '\u2640'  # female symbol
    elif gender == 3:
        return '\u26b2'  # neutral
    return '?'  # catch all


# Returns True if the pokemon is shiny in the wild
def get_shiny_status(pokemon_id, form_id):
    if not hasattr(get_shiny_status, 'info'):
        get_shiny_status.info = {}
        file_ = get_path('data/shiny_data.json')
        with open(file_, 'r') as f:
            j = json.load(f)
            f.close()
        for id_form_id_ in j:
            if '*' not in id_form_id_ and j[id_form_id_] == ' \u2728':
                get_shiny_status.info[id_form_id_] = True

    return (get_shiny_status.info.get(f'{pokemon_id}', False)
            or get_shiny_status.info.get(f'{pokemon_id}_{form_id}', False))

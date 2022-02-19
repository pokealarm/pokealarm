# Standard Library Imports
import json
# 3rd Party Imports
# Local Imports
from PokeAlarm.Utils import get_path


# Returns True if the pokemon is shiny in raids
def get_raid_shiny_status(pokemon_id):
    if not hasattr(get_raid_shiny_status, 'info'):
        get_raid_shiny_status.info = {}
        file_ = get_path('data/shiny_data.json')
        with open(file_, 'r') as f:
            j = json.load(f)
            f.close()
        for id_ in j:
            get_raid_shiny_status.info[int(id_)] = j[id_].get('found_raid')

    return get_raid_shiny_status.info.get(pokemon_id, False)


# Returns shiny symbol if the pokemon is shiny in raids
def get_raid_shiny_emoji(pokemon_id):
    if get_raid_shiny_status(pokemon_id):
        return '✨'
    else:
        return ''

# Standard Library Imports
from glob import glob
import json
# 3rd Party Imports
# Local Imports
from PokeAlarm.Utils import get_path


# Returns the id corresponding with the team name
# (use all locales for flexibility)
def get_team_id(team_name):
    try:
        name = str(team_name).lower()
        if not hasattr(get_team_id, 'ids'):
            get_team_id.ids = {}
            files = glob(get_path('locales/*.json'))
            for file_ in files:
                with open(file_, 'r') as f:
                    j = json.loads(f.read())
                    j = j['teams']
                    for id_ in j:
                        nm = j[id_].lower()
                        get_team_id.ids[nm] = int(id_)
        if name in get_team_id.ids:
            return get_team_id.ids[name]
        else:
            return int(name)  # try as an integer
    except ValueError:
        raise ValueError("Unable to interpret `{}` as a valid "
                         " team name or id.".format(team_name))


# Returns true if the string matches any given RE objects
def match_regex_dict(reg_exs, name):
    name = str(name)
    for reg_ex in reg_exs:
        if reg_ex.search(name):
            return True
    return False

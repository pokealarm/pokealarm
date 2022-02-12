# -*- coding: utf-8 -*-
# Standard Library Imports
from datetime import datetime, timedelta
from glob import glob
import json
import logging
from math import radians, sin, cos, atan2, sqrt, degrees
import os
import sys
# 3rd Party Imports
# Local Imports
from PokeAlarm import not_so_secret_url
from PokeAlarm import config
from PokeAlarm import Unknown

log = logging.getLogger('Utils')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ SYSTEM UTILITIES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Checks is a line contains any substitutions located in args
def contains_arg(line, args):
    for word in args:
        if ('<' + word + '>') in line:
            return True
    return False


def get_path(path):
    if not os.path.isabs(path):  # If not absolute path
        path = os.path.join(config['ROOT_PATH'], path)
    return path


def parse_boolean(val):
    b = str(val).lower()
    if b in {'t', 'true', 'y', 'yes'}:
        return True
    if b in ('f', 'false', 'n', 'no'):
        return False
    return None


# Used for lazy installs - installs required module with pip
def pip_install(req, version):
    import subprocess
    target = "{}=={}".format(req, version)
    log.info("Attempting to pip install %s..." % target)
    subprocess.call(['pip', 'install', target])
    log.info("%s install complete." % target)


# Used to exit when leftover parameters are found
def reject_leftover_parameters(dict_, location):
    if len(dict_) > 0:
        log.error("Unknown parameters at {}: ".format(location))
        log.error(list(dict_.keys()))
        log.error("Please consult the PokeAlarm wiki for accepted parameters.")
        sys.exit(1)


# Load a key from the given dict, or throw an error if it isn't there
def require_and_remove_key(key, _dict, location):
    if key in _dict:
        return _dict.pop(key)
    else:
        log.error("The parameter '{}' is required for {}".format(key, location)
                  + " Please check the PokeAlarm wiki for correct formatting.")
        sys.exit(1)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ POKEMON UTILITIES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# Returns the id corresponding with the pokemon name
# (use all locales for flexibility)
def get_pkmn_id(pokemon_name):
    name = pokemon_name.lower()
    if not hasattr(get_pkmn_id, 'ids'):
        get_pkmn_id.ids = {}
        files = glob(get_path('locales/*.json'))
        for file_ in files:
            with open(file_, 'r') as f:
                j = json.loads(f.read())
                j = j['pokemon']
                for id_ in j:
                    nm = j[id_].lower()
                    get_pkmn_id.ids[nm] = int(id_)
    return get_pkmn_id.ids.get(name)


# Returns the id corresponding with the move (use all locales for flexibility)
def get_move_id(move_name):
    name = move_name.lower()
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
    return get_move_id.ids.get(name)


# Returns the id corresponding with the pokemon name
# (use all locales for flexibility)
def get_team_id(team_name):
    name = team_name.lower()
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
    return get_team_id.ids.get(name)


# Returns the types of a move when requesting
def get_move_type(move_id):
    if not hasattr(get_move_type, 'info'):
        get_move_type.info = {}
        file_ = get_path('data/move_info.json')
        with open(file_, 'r') as f:
            j = json.loads(f.read())
        for id_ in j:
            get_move_type.info[int(id_)] = j[id_]['type']
    return get_move_type.info.get(move_id, Unknown.SMALL)


# Returns the damage of a move when requesting
def get_move_damage(move_id):
    if not hasattr(get_move_damage, 'info'):
        get_move_damage.info = {}
        file_ = get_path('data/move_info.json')
        with open(file_, 'r') as f:
            j = json.loads(f.read())
        for id_ in j:
            get_move_damage.info[int(id_)] = j[id_]['damage']
    return get_move_damage.info.get(move_id, 'unkn')


# Returns the dps of a move when requesting
def get_move_dps(move_id):
    if not hasattr(get_move_dps, 'info'):
        get_move_dps.info = {}
        file_ = get_path('data/move_info.json')
        with open(file_, 'r') as f:
            j = json.loads(f.read())
        for id_ in j:
            get_move_dps.info[int(id_)] = j[id_]['dps']
    return get_move_dps.info.get(move_id, 'unkn')


# Returns the duration of a move when requesting
def get_move_duration(move_id):
    if not hasattr(get_move_duration, 'info'):
        get_move_duration.info = {}
        file_ = get_path('data/move_info.json')
        with open(file_, 'r') as f:
            j = json.loads(f.read())
        for id_ in j:
            get_move_duration.info[int(id_)] = j[id_]['duration']
    return get_move_duration.info.get(move_id, 'unkn')


# Returns the duration of a move when requesting
def get_move_energy(move_id):
    if not hasattr(get_move_energy, 'info'):
        get_move_energy.info = {}
        file_ = get_path('data/move_info.json')
        with open(file_, 'r') as f:
            j = json.loads(f.read())
        for id_ in j:
            get_move_energy.info[int(id_)] = j[id_]['energy']
    return get_move_energy.info.get(move_id, 'unkn')


# Returns the base height for a pokemon
def get_base_height(pokemon_id):
    if not hasattr(get_base_height, 'info'):
        get_base_height.info = {}
        file_ = get_path('data/base_stats.json')
        with open(file_, 'r') as f:
            j = json.loads(f.read())
        for id_ in j:
            get_base_height.info[int(id_)] = j[id_].get('height')
    return get_base_height.info.get(pokemon_id)


# Returns the base weight for a pokemon
def get_base_weight(pokemon_id):
    if not hasattr(get_base_weight, 'info'):
        get_base_weight.info = {}
        file_ = get_path('data/base_stats.json')
        with open(file_, 'r') as f:
            j = json.loads(f.read())
        for id_ in j:
            get_base_weight.info[int(id_)] = j[id_].get('weight')
    return get_base_weight.info.get(pokemon_id)


# Returns the base stats for a pokemon
def get_base_stats(pokemon_id):
    if not hasattr(get_base_stats, 'info'):
        get_base_stats.info = {}
        file_ = get_path('data/base_stats.json')
        with open(file_, 'r') as f:
            j = json.loads(f.read())
        for id_ in j:
            get_base_stats.info[int(id_)] = {
                "attack": float(j[id_].get('attack')),
                "defense": float(j[id_].get('defense')),
                "stamina": float(j[id_].get('stamina'))
            }

    return get_base_stats.info.get(pokemon_id)


# Returns possible evolutions for a pokemon
def get_evolutions(pokemon_id):
    if not hasattr(get_evolutions, 'info'):
        get_evolutions.info = {}
        file_ = get_path('data/base_stats.json')
        with open(file_, 'r') as f:
            j = json.loads(f.read())
        for id_ in j:
            get_evolutions.info[int(id_)] = j[id_].get('evolutions')
    return get_evolutions.info.get(pokemon_id)


# Return CP multipliers
def get_cp_multipliers():
    if not hasattr(get_cp_multipliers, 'info'):
        file_ = get_path('data/cp_multipliers.json')
        with open(file_, 'r') as f:
            get_cp_multipliers.info = json.load(f)
    return get_cp_multipliers.info


# Returns the highest possible stat product for PvP great league for a pkmn
def get_great_product(pokemon_id):
    if not hasattr(get_great_product, 'info'):
        get_great_product.info = {}
        file_ = get_path('data/base_stats.json')
        with open(file_, 'r') as f:
            j = json.loads(f.read())
        for id_ in j:
            get_great_product.info[int(id_)] = j[id_].get('1500_product')

    return get_great_product.info.get(pokemon_id)


# Returns the highest possible stat product for PvP ultra league for a pkmn
def get_ultra_product(pokemon_id):
    if not hasattr(get_ultra_product, 'info'):
        get_ultra_product.info = {}
        file_ = get_path('data/base_stats.json')
        with open(file_, 'r') as f:
            j = json.loads(f.read())
        for id_ in j:
            get_ultra_product.info[int(id_)] = j[id_].get('2500_product')

    return get_ultra_product.info.get(pokemon_id)


# Returns a cp range for a certain level of a pokemon caught in a raid
def get_pokemon_cp_range(pokemon_id, level):
    stats = get_base_stats(pokemon_id)

    if not hasattr(get_pokemon_cp_range, 'info'):
        get_pokemon_cp_range.info = {}
        file_ = get_path('data/cp_multipliers.json')
        with open(file_, 'r') as f:
            j = json.loads(f.read())
        for lvl_ in j:
            get_pokemon_cp_range.info[lvl_] = j[lvl_]

    cp_multi = get_pokemon_cp_range.info["{}".format(level)]

    # minimum IV for a egg/raid pokemon is 10/10/10
    min_cp = int(
        ((stats['attack'] + 10.0) * pow((stats['defense'] + 10.0), 0.5)
         * pow((stats['stamina'] + 10.0), 0.5) * pow(cp_multi, 2)) / 10.0)
    max_cp = int(
        ((stats['attack'] + 15.0) * pow((stats['defense'] + 15.0), 0.5) *
         pow((stats['stamina'] + 15.0), 0.5) * pow(cp_multi, 2)) / 10.0)

    return min_cp, max_cp


# Returns the size ratio of a pokemon
def size_ratio(pokemon_id, height, weight):
    height_ratio = height / get_base_height(pokemon_id)
    weight_ratio = weight / get_base_weight(pokemon_id)
    return height_ratio + weight_ratio


# Returns the appraised size_id of a pokemon
def get_pokemon_size(pokemon_id, height, weight):
    size = size_ratio(pokemon_id, height, weight)
    if size < 1.5:
        return 1
    elif size <= 1.75:
        return 2
    elif size <= 2.25:
        return 3
    elif size <= 2.5:
        return 4
    else:
        return 5


# Returns the gender symbol of a pokemon:
def get_pokemon_gender(gender):
    if gender == 1:
        return '\u2642'  # male symbol
    elif gender == 2:
        return '\u2640'  # female symbol
    elif gender == 3:
        return '\u26b2'  # neutral
    return '?'  # catch all


# Returns the types for a pokemon
def get_base_types(pokemon_id):
    if not hasattr(get_base_types, 'info'):
        get_base_types.info = {}
        file_ = get_path('data/base_stats.json')
        with open(file_, 'r') as f:
            j = json.loads(f.read())
            for id_ in j:
                get_base_types.info[int(id_)] = [
                    j[id_].get('type1'),
                    j[id_].get('type2')
                ]
    return get_base_types.info.get(pokemon_id)


# Returns the types for a pokemon
def get_mon_type(pokemon_id):
    types = get_base_types(pokemon_id)
    return types['type1'], types['type2']


# Return a boolean for whether the raid boss will have it's catch CP boosted
def is_weather_boosted(pokemon_id, weather_id):
    if not hasattr(is_weather_boosted, 'info'):
        is_weather_boosted.info = {}
        file_ = get_path('data/weather_boosts.json')
        with open(file_, 'r') as f:
            j = json.loads(f.read())
        for w_id in j:
            is_weather_boosted.info[w_id] = j[w_id]

    boosted_types = is_weather_boosted.info.get(str(weather_id), {})
    types = get_base_types(pokemon_id)
    return types[0] in boosted_types or types[1] in boosted_types


def weather_id_is_boosted(desired_status, weather_id):
    if desired_status is True and weather_id != 0 and weather_id is not None:
        return True
    if desired_status is False and (weather_id == 0 or weather_id is None):
        return True
    return False


def get_weather_emoji(weather_id):
    return {
        1: '☀️',
        2: '☔️',
        3: '⛅',
        4: '☁️',
        5: '💨',
        6: '⛄️',
        7: '🌁',
    }.get(weather_id, '')


def get_type_emoji(type_id):
    return {
        1: '⭕',
        2: '🥋',
        3: '🐦',
        4: '☠',
        5: '⛰️',
        6: '💎',
        7: '🐛',
        8: '👻',
        9: '⚙',
        10: '🔥',
        11: '💧',
        12: '🍃',
        13: '⚡',
        14: '🔮',
        15: '❄',
        16: '🐲',
        17: '💫',
        18: '🌑'
    }.get(type_id, '')


def get_spawn_verified_emoji(spawn_verified_id):
    return {
        0: '❌',
        1: '✅',
    }.get(spawn_verified_id, '❔')


def get_team_emoji(team_id):
    return {
        0: '⚪',
        1: '🔵',
        2: '🔴',
        3: '🟡',
    }.get(team_id, '❔')


def get_ex_eligible_emoji(ex_eligible):
    return {
        0: '',
        1: '✉️',
    }.get(ex_eligible, '')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ GMAPS API UTILITIES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# Returns a String link to Google Maps Pin at the location
def get_gmaps_link(lat, lng, nav):
    _nav = 'dir' if nav else 'search'
    latlng = '{:5f}%2C{:5f}'.format(lat, lng)
    return 'https://www.google.com/maps/{}/?api=1'.format(_nav) \
        + '&destination={}'.format(latlng)


# Returns a String link to Apple Maps Pin at the location
def get_applemaps_link(lat, lng, nav):
    _nav = 'daddr' if nav else 'address'
    latlng = '{:5f}%2C{:5f}'.format(lat, lng)
    return 'https://maps.apple.com/maps?{}={}&t=m'.format(_nav,latlng)


# Returns a String link to Waze Maps Navigation at the location
def get_waze_link(lat, lng, nav):
    _nav = 'yes' if nav else 'no'
    latlng = '{:5f}%2C{:5f}'.format(lat, lng)
    return 'https://waze.com/ul?navigate={}&ll={}'.format(_nav,latlng)


# Returns a static map url with <lat> and <lng> parameters for dynamic test
def get_static_map_url(settings, api_key=None):  # TODO: optimize formatting
    if not parse_boolean(settings.get('enabled', 'True')):
        return None
    width = settings.get('width', '250')
    height = settings.get('height', '125')
    maptype = settings.get('maptype', 'roadmap')
    zoom = settings.get('zoom', '15')

    center = '{}%2C{}'.format('<lat>', '<lng>')
    query_center = 'center={}'.format(center)
    query_markers = 'markers=color:red%7C{}'.format(center)
    query_size = 'size={}x{}'.format(width, height)
    query_zoom = 'zoom={}'.format(zoom)
    query_maptype = 'maptype={}'.format(maptype)

    map_ = ('https://www.google.com/maps/api/staticmap?maptype=roadmap' +
            query_center + '&' + query_markers + '&' +
            query_maptype + '&' + query_size + '&' + query_zoom)

    if api_key is not None:
        map_ += ('&key=%s' % api_key)
        # log.debug("API_KEY added to static map url.")
    return map_


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ GENERAL UTILITIES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


# Returns a cardinal direction (N/NW/W/SW, etc)
# of the pokemon from the origin point, if set
def get_cardinal_dir(pt_a, pt_b=None):
    if pt_b is None:
        return '?'

    lat1, lng1, lat2, lng2 = map(radians, [pt_b[0], pt_b[1], pt_a[0], pt_a[1]])
    directions = ["S", "SE", "E", "NE", "N", "NW", "W", "SW", "S"]
    bearing = (degrees(atan2(
        cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(lng2 - lng1),
        sin(lng2 - lng1) * cos(lat2))) + 450) % 360
    return directions[int(round(bearing / 45))]


# Return the distance formatted correctly
def get_dist_as_str(dist, units):
    if units == 'imperial':
        if dist > 1760:  # yards per mile
            return "{:.1f}mi".format(dist / 1760.0)
        else:
            return "{:.1f}yd".format(dist)
    else:  # Metric
        if dist > 1000:  # meters per km
            return "{:.1f}km".format(dist / 1000.0)
        else:
            return "{:.1f}m".format(dist)


# Returns an integer representing the distance between A and B
def get_earth_dist(pt_a, pt_b=None, units='imperial'):
    if type(pt_a) is str or pt_b is None:
        return 'unkn'  # No location set
    lat_a = radians(pt_a[0])
    lng_a = radians(pt_a[1])
    lat_b = radians(pt_b[0])
    lng_b = radians(pt_b[1])
    lat_delta = lat_b - lat_a
    lng_delta = lng_b - lng_a
    a = sin(lat_delta / 2) ** 2 + cos(lat_a) * \
        cos(lat_b) * sin(lng_delta / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    radius = 6373000  # radius of earth in meters
    if units == 'imperial':
        radius = 6975175  # radius of earth in yards
    dist = c * radius
    return dist


# Return the time as a string in different formats
def get_time_as_str(t, timezone=None):
    if timezone is None:
        timezone = config.get("TIMEZONE")
    s = (t - datetime.utcnow()).total_seconds()
    (m, s) = divmod(s, 60)
    (h, m) = divmod(m, 60)
    d = timedelta(hours=h, minutes=m, seconds=s)
    if timezone is not None:
        disappear_time = datetime.now(tz=timezone) + d
    else:
        disappear_time = datetime.now() + d
    # Time remaining in minutes and seconds
    time = "%dm %ds" % (m, s) if h == 0 else "%dh %dm" % (h, m)
    # Disappear time in 12h format, eg "2:30:16 PM"
    time_12h = disappear_time.strftime("%I:%M:%S") \
        + disappear_time.strftime("%p").lower()
    # Disappear time in 24h format including seconds, eg "14:30:16"
    time_24h = disappear_time.strftime("%H:%M:%S")

    # Get the same as above but without seconds
    time_no_sec = "%dm" % m if h == 0 else "%dh %dm" % (h, m)
    time_12h_no_sec = disappear_time.strftime("%I:%M") \
        + disappear_time.strftime("%p").lower()
    time_24h_no_sec = disappear_time.strftime("%H:%M")

    time_raw_hours = int(h)
    time_raw_minutes = int(m)
    time_raw_seconds = int(s)

    return time, time_12h, time_24h, \
        time_no_sec, time_12h_no_sec, time_24h_no_sec, \
        time_raw_hours, time_raw_minutes, time_raw_seconds


# Return the time in seconds
def get_seconds_remaining(t, timezone=None):
    if timezone is None:
        timezone = config.get("TIMEZONE")
    seconds = (t - datetime.utcnow()).total_seconds()
    return seconds


# Return the default url for images and stuff
def get_image_url(suffix):
    return not_so_secret_url + suffix


# Returns the id corresponding with the weather
# (use all locales for flexibility)
def get_weather_id(weather_name):
    try:
        name = str(weather_name).lower()
        if not hasattr(get_weather_id, 'ids'):
            get_weather_id.ids = {}
            files = glob(get_path('locales/*.json'))
            for file_ in files:
                with open(file_, 'r') as f:
                    j = json.loads(f.read())
                    j = j['weather']
                    for id_ in j:
                        nm = j[id_].lower()
                        get_weather_id.ids[nm] = int(id_)
        if name in get_weather_id.ids:
            return get_weather_id.ids[name]
        else:
            return int(name)  # try as an integer
    except ValueError:
        raise ValueError("Unable to interpret `{}` as a valid "
                         " weather name or id.".format(weather_name))


# Returns true if any item is in the provided list
def match_items_in_array(list, items):
    for obj in list:
        if obj in items:
            return True
    return False

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

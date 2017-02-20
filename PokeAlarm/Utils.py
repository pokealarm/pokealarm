# Standard Library Imports
from datetime import datetime, timedelta
from glob import glob
import json
import logging
from math import radians, sin, cos, atan2, sqrt
import os
import sys
# 3rd Party Imports
from s2sphere import LatLng
# Local Imports
from . import config

log = logging.getLogger('Utils')


################################################### SYSTEM UTILITIES ###################################################

# Checks is a line contains any subsititions located in args
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


def parse_unicode(bytestring):
    decoded_string = bytestring.decode(sys.getfilesystemencoding())
    return decoded_string


# Used for lazy installs - installs required module with pip
def pip_install(module, version):
    import subprocess
    target = "{}=={}".format(module, version)
    log.info("Attempting to pip install %s..." % target)
    subprocess.call(['pip', 'install', target])
    log.info("%s install complete." % target)


########################################################################################################################

################################################## POKEMON UTILITIES ###################################################

# Returns the id corresponding with the pokemon name (use all locales for flexibility)
def get_pkmn_id(pokemon_name):
    name = pokemon_name.lower()
    if not hasattr(get_pkmn_id, 'ids'):
        get_pkmn_id.ids = {}
        files = glob(get_path('locales/*/pokemon.json'))
        for file_ in files:
            with open(file_, 'r') as f:
                j = json.loads(f.read())
                for id_ in j:
                    nm = j[id_].lower()
                    get_pkmn_id.ids[nm] = int(id_)
    return get_pkmn_id.ids.get(name)


# Returns the id corresponding with the move (use all locales for flexibility)
def get_move_id(move_name):
    name = move_name.lower()
    if not hasattr(get_move_id, 'ids'):
        get_move_id.ids = {}
        files = glob(get_path('locales/*/moves.json'))
        for file_ in files:
            with open(file_, 'r') as f:
                j = json.loads(f.read())
                for id_ in j:
                    nm = j[id_].lower()
                    get_move_id.ids[nm] = int(id_)
    return get_move_id.ids.get(name)


# Returns the id corresponding with the pokemon name (use all locales for flexibility)
def get_team_id(pokemon_name):
    name = pokemon_name.lower()
    if not hasattr(get_team_id, 'ids'):
        get_team_id.ids = {}
        files = glob(get_path('locales/*/teams.json'))
        for file_ in files:
            with open(file_, 'r') as f:
                j = json.loads(f.read())
                for id_ in j:
                    nm = j[id_].lower()
                    get_team_id.ids[nm] = int(id_)
    return get_team_id.ids.get(name)


# Returns the damage of a move when requesting
def get_move_damage(move_id):
    if not hasattr(get_move_damage, 'info'):
        get_move_damage.info = {}
        file_ = get_path('locales/move_info.json')
        with open(file_, 'r') as f:
            j = json.loads(f.read())
        for id_ in j:
            get_move_damage.info[int(id_)] = j[id_]['damage']
    return get_move_damage.info.get(move_id, 'unkn')


# Returns the dps of a move when requesting
def get_move_dps(move_id):
    if not hasattr(get_move_dps, 'info'):
        get_move_dps.info = {}
        file_ = get_path('locales/move_info.json')
        with open(file_, 'r') as f:
            j = json.loads(f.read())
        for id_ in j:
            get_move_dps.info[int(id_)] = j[id_]['dps']
    return get_move_dps.info.get(move_id, 'unkn')


# Returns the duration of a move when requesting
def get_move_duration(move_id):
    if not hasattr(get_move_duration, 'info'):
        get_move_duration.info = {}
        file_ = get_path('locales/move_info.json')
        with open(file_, 'r') as f:
            j = json.loads(f.read())
        for id_ in j:
            get_move_duration.info[int(id_)] = j[id_]['duration']
    return get_move_duration.info.get(move_id, 'unkn')

# Returns the duation of a move when requesting
def get_move_energy(move_id):
    if not hasattr(get_move_energy, 'info'):
        get_move_energy.info = {}
        file_ = get_path('locales/move_info.json')
        with open(file_, 'r') as f:
            j = json.loads(f.read())
        for id_ in j:
            get_move_energy.info[int(id_)] = j[id_]['energy']
    return get_move_energy.info.get(move_id, 'unkn')



########################################################################################################################

################################################# GMAPS API UTILITIES ##################################################

# Returns a String link to Google Maps Pin at the location
def get_gmaps_link(lat, lng):
    latlng = '{},{}'.format(repr(lat), repr(lng))
    return 'http://maps.google.com/maps?q={}'.format(latlng)

# Returns a static map url with <lat> and <lng> parameters for dynamic test
def get_static_map_url(settings):  # TODO: optimize formatting
    if not parse_boolean(settings.get('enabled', 'True')):
        return None
    width = settings.get('width', '250')
    height = settings.get('height', '125')
    maptype = settings.get('maptype', 'roadmap')
    zoom = settings.get('zoom', '15')

    center = '{},{}'.format('<lat>', '<lng>')
    query_center = 'center={}'.format(center)
    query_markers = 'markers=color:red%7C{}'.format(center)
    query_size = 'size={}x{}'.format(width, height)
    query_zoom = 'zoom={}'.format(zoom)
    query_maptype = 'maptype={}'.format(maptype)

    map_ = ('https://maps.googleapis.com/maps/api/staticmap?' +
            query_center + '&' + query_markers + '&' +
            query_maptype + '&' + query_size + '&' + query_zoom)

    if config['API_KEY'] is not None:
        map_ += ('&key=%s' % config['API_KEY'])
        log.debug("API_KEY added to static map url.")
    return map_


########################################################################################################################

################################################## GENERAL UTILITIES ###################################################

# Returns a cardinal direction (N/S/E/W) of the pokemon from the origin point, if set
def get_cardinal_dir(pt_a, pt_b=None):
    if pt_b is None:
        return '?'
    origin_point = LatLng.from_degrees(*pt_b)
    lat_lng = LatLng.from_degrees(*pt_a)
    diff = lat_lng - origin_point
    diff_lat = diff.lat().degrees
    diff_lng = diff.lng().degrees
    direction = (('N' if diff_lat >= 0 else 'S') if abs(diff_lat) > 1e-4 else '') + \
                (('E' if diff_lng >= 0 else 'W') if abs(diff_lng) > 1e-4 else '')
    return direction


# Return the distance formatted correctly
def get_dist_as_str(dist):
    if config['UNITS'] == 'imperial':
        if dist > 1000:
            return "{:.1f}mi".format(dist / 1760)
        else:
            return "{:.1f}yd".format(dist)
    else:  # Metric
        if dist > 1760:
            return "{:.1f}km".format(dist / 1000)
        else:
            return "{:.1f}m".format(dist)


# Returns an integer representing the distance between A and B
def get_earth_dist(pt_a, pt_b=None):
    if pt_b == None:
        return 'unkn'  # No location set
    lat_a = radians(pt_a[0])
    lng_a = radians(pt_a[1])
    lat_b = radians(pt_b[0])
    lng_b = radians(pt_b[1])
    lat_delta = lat_b - lat_a
    lng_delta = lng_b - lng_a
    a = sin(lat_delta / 2) ** 2 + cos(lat_a) * cos(lat_b) * sin(lng_delta / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    radius = 6373000  # radius of earth in meters
    if config['UNITS'] == 'imperial':
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
    time_left = "%dm %ds" % (m, s)
    # Dissapear time in 12h format, eg "2:30:16 PM"
    time_12 = disappear_time.strftime("%I:%M:%S") + disappear_time.strftime("%p").lower()
    # Dissapear time in 24h format including seconds, eg "14:30:16"
    time_24 = disappear_time.strftime("%H:%M:%S")
    return time_left, time_12, time_24

########################################################################################################################

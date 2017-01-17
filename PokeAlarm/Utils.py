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

# Returns a String link to Google Maps Pin at the location
def get_gmaps_link(lat, lng):
    latlng = '{},{}'.format(repr(lat), repr(lng))
    return 'http://maps.google.com/maps?q={}'.format(latlng)


# Returns the id corresponding with the pokemon name (use all locales for flexibility)
def get_pkmn_id(pokemon_name):
    name = pokemon_name.lower()
    if not hasattr(get_pkmn_id, 'ids'):
        get_pkmn_id.ids = {}
        files = glob(get_path('locales/*/pokemon.json'))
        for file in files:
            with open(file, 'r') as f:
                j = json.loads(f.read())
                for id in j:
                    nm = j[id].lower()
                    get_pkmn_id.ids[nm] = int(id)
    return get_pkmn_id.ids.get(name)


# Returns the id corresponding with the pokemon name (use all locales for flexibility)
def get_team_id(pokemon_name):
    name = pokemon_name.lower()
    if not hasattr(get_team_id, 'ids'):
        get_team_id.ids = {}
        files = glob(get_path('locales/*/teams.json'))
        for file in files:
            with open(file, 'r') as f:
                j = json.loads(f.read())
                for id in j:
                    nm = j[id].lower()
                    get_team_id.ids[nm] = int(id)
    return get_team_id.ids.get(name)


########################################################################################################################

################################################# GMAPS API UTILITIES ##################################################


# Returns a static map url with <lat> and <lng> parameters for dynamic test
def get_static_map_url(settings):
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

    map = ('https://maps.googleapis.com/maps/api/staticmap?' +
           query_center + '&' + query_markers + '&' +
           query_maptype + '&' + query_size + '&' + query_zoom)

    if 'API_KEY' in config:
        map += ('&key=%s' % config['API_KEY'])
        log.debug("API_KEY added to static map url.")
    return map


########################################################################################################################

################################################## GENERAL UTILITIES ###################################################

# Returns a cardinal direction (N/S/E/W) of the pokemon from the origin point, if set
def get_cardinal_dir(ptA, ptB):
    if ptB is None:
        return '?'
    origin_point = LatLng.from_degrees(*ptB)
    lat_lng = LatLng.from_degrees(*ptA)
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
            return "{:.1f}km".format(dist / 1000)
        else:
            return "{:.1f}m".format(dist)
    else:  # Metric
        if dist > 1760:
            return "{:.1f}km".format(dist / 1760)
        else:
            return "{:.1f}m".format(dist)


# Returns an integer representing the distance between A and B
def get_earth_dist(ptA, ptB):
    if ptB is None:
        return 'unkn'  # No location set
    lat_a = radians(ptA[0])
    lng_a = radians(ptA[1])
    lat_b = radians(ptB[0])
    lng_b = radians(ptB[1])
    dLat = lat_b - lat_a
    dLng = lng_b - lng_a
    a = sin(dLat / 2) ** 2 + cos(lat_a) * cos(lat_b) * sin(dLng / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    radius = 6373000  # radius of earth in meters
    if config['UNITS'] == 'imperial':
        radius = 6975175  # radius of earth in yards
    dist = c * radius
    return dist


# Return the time as a string in different formats
def get_time_as_str(t, timezone=None):
    s = (t - datetime.utcnow()).total_seconds()
    (m, s) = divmod(s, 60)
    (h, m) = divmod(m, 60)
    d = timedelta(hours=h, minutes=m, seconds=s)
    if timezone is not None:
        disappear_time = datetime.now(tz=config.get("TIMEZONE")) + d
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

#Logging
import logging
log = logging.getLogger(__name__)

#Python Utility imports
import os
import json
import configargparse
import time
import sys
import re
import googlemaps
import pytz
from glob import glob
from datetime import datetime, timedelta
from math import radians, sin, cos, atan2, sqrt
from s2sphere import LatLng

#Local imports
from . import config
from geofence import Geofence

########################## GENERAL UTILITIES #########################

def parse_unicode(bytestring):
    decoded_string = bytestring.decode(sys.getfilesystemencoding())
    return decoded_string
	
def parse_boolean(val):
	b = str(val).lower()
	if b in {'t', 'true', 'y', 'yes'}:
		return True
	if b in ('f', 'false', 'n', 'no'):
		return False
	return None
	
def get_path(path):
	if not os.path.isabs(path): #If not absolute path
		path = os.path.join(config['ROOT_PATH'], path)
	return path

#Attempts to send the alert with the specified args, reconnecting if neccesary	
def try_sending(alarmLog, reconnect, name, send_alert, args):
	for i in range(1,6):
		try:
			send_alert(**args)
			if i is not 1:
				log.info("%s successly reconnected." % name)
			return #message sent succesfull
		except Exception as e:
			alarmLog.error(e)
			alarmLog.error("%s is having connection issues. %d attempt of 5." % (name, i))
			time.sleep(5)
			reconnect()
	alarmLog.error("Could not connect to %s... Giving up." % name)

#Used for lazy installs - installs required module with pip
def pip_install(module, version):
	import pip
	import subprocess
	target = "{}=={}".format(module, version)
	log.info("Attempting to pip install %s..." % target)
	subprocess.call(['pip', 'install', target])
	log.info("%s install complete." % target)

#####################################################################

########################## CONFIG UTILITIES #########################	
def set_config(root_path):
	config['ROOT_PATH'] = root_path
	configpath = get_path('config/config.ini')
	parser = configargparse.ArgParser(default_config_files=[configpath])
	parser.add_argument('-H', '--host', help='Set web server listening host', default='127.0.0.1')
	parser.add_argument('-P', '--port', type=int, help='Set web server listening port', default=4000)
	parser.add_argument('-k', '--key', help='Specify a Google Maps API Key to use.')
	parser.add_argument('-c', '--config', help='Alarms configuration file. default: alarms.json', default='alarms.json')
	parser.add_argument('-l', '--location', type=parse_unicode, help='Location, can be an address or coordinates')
	parser.add_argument('-L', '--locale', help='Locale for Pokemon names: default en, check locale folder for more options', default='en')
	parser.add_argument('-u' , '--units',  help='Specify either metric or imperial . Default: metric', choices=['metric', 'imperial'], default='metric')
	parser.add_argument('-d', '--debug', help='Debug Mode', action='store_true',  default=False)
	parser.add_argument('-gf', '--geofence', help='Specify a file of coordinates, limiting alerts to within this area')
	parser.add_argument('-tl', '--timelimit', type=int, help='Minimum number of seconds remaining on a pokemon to notify', default=0)
	parser.add_argument('-tz', '--timezone', help='Timezone used for notifications.  Ex: "America/Los_Angeles"')
	
	args = parser.parse_args()
	
	config['HOST'] = args.host
	config['PORT'] = args.port
	config['CONFIG_FILE'] = args.config
	config['LOCALE'] = args.locale
	config['DEBUG'] = args.debug
	config['UNITS'] = args.units
	config['TIME_LIMIT'] = args.timelimit
	
	if args.key:
		config['API_KEY'] = key=args.key
		config['GMAPS_CLIENT'] = googlemaps.Client(key=args.key)
	
	if args.location:
		config['LOCATION'] =  get_pos_by_name(args.location)
	
	if args.geofence:
		config['GEOFENCE'] = Geofence(os.path.join(root_path, args.geofence))

	if args.timezone:
		try:
			config['TIMEZONE'] = pytz.timezone(args.timezone)
			log.info("Timezone set to: %s" % args.timezone)
		except pytz.exceptions.UnknownTimeZoneError:
			log.error("Invalid timezone. For a list of valid timezones, see https://en.wikipedia.org/wiki/List_of_tz_database_time_zones")
			sys.exit(1)

	config['REV_LOC'] = False
	config['DM_WALK'] = False
	config['DM_BIKE'] = False
	config['DM_DRIVE'] = False
	
	return config

#Returns +inf if True, else float, else None
def parse_alert_param(value):
	v = None
	if parse_boolean(value):
			v = float('inf')
	else:
		try:
			v = float(value)
		except ValueError:
			log.debug("Alert Param: Unable to parse into float")
	return v

def make_pokestops_list(settings):
	notify = {}
	if 'Lured' in settings:
		notify['lured'] = parse_alert_param(settings['Lured'])
	return notify

def make_gym_list(settings):
	notify = {}
	for key in settings:
		param = parse_alert_param(settings[key])
		if param is not None:
			notify[key] = param
	return notify
		
#########################################################################

############################# INFO UTILITIES ############################
	
#Returns the id corresponding with the pokemon name
def get_pkmn_id(pokemon_name):
	name = pokemon_name.lower()
	if not hasattr(get_pkmn_id, 'ids'):
		get_pkmn_id.ids = {}
		files = glob(os.path.join( config['ROOT_PATH'],config['LOCALES_DIR'],'pokemon.*.json'))
		for file in files:
			with open(file, 'r') as f:
				j = json.loads(f.read())
				for id in j:
					nm = j[id].lower()
					get_pkmn_id.ids[nm] = int(id)
	return get_pkmn_id.ids.get(name)

#Returns a String represnting the name of the pokemon from the set LOCALE
def get_pkmn_name(pokemon_id):
    if not hasattr(get_pkmn_name, 'names'):
        file_path = os.path.join( config['ROOT_PATH'], config['LOCALES_DIR'],
            'pokemon.{}.json'.format(config['LOCALE']))
        with open(file_path, 'r') as f:
            get_pkmn_name.names = json.loads(f.read())
    return get_pkmn_name.names.get(str(pokemon_id)).encode("utf-8")
	
#Test for Movesets
def get_pkmn_move(move_id):
    if not hasattr(get_pkmn_move, 'moves'):
        file_path = os.path.join( config['ROOT_PATH'], config['LOCALES_DIR'],
            'moves.{}.json'.format(config['LOCALE']))
        with open(file_path, 'r') as f:
            get_pkmn_move.moves = json.loads(f.read())
    return str(get_pkmn_move.moves.get(str(move_id))).encode("utf-8")

_gym_names = {0:"Neutral", 1:"Mystic", 2:"Valor", 3:"Instinct"}
def get_team_name(team_number):
    return _gym_names[team_number]
	
#Returns a String link to Google Maps Pin at the location	
def get_gmaps_link(lat, lng):
	latLon = '{},{}'.format(repr(lat), repr(lng))
	return 'http://maps.google.com/maps?q={}'.format(latLon)
	
#Return a version of the string with the correct substitutions made	
def replace(string, pkinfo):
	s = string.encode('utf-8')
	for key in pkinfo:
		s = s.replace("<{}>".format(key), str(pkinfo[key]))
	return s

#Returns a cardinal direction (N/S/E/W) of the pokemon from the origin point, if set
def get_dir(lat, lng):
	origin_point = config.get("LOCATION")
	if origin_point is None:
		return "NoLocationSet" #No location set
	origin_point = LatLng.from_degrees(origin_point[0], origin_point[1])
	latLon = LatLng.from_degrees(lat, lng)
	diff = latLon - origin_point
	diff_lat = diff.lat().degrees
	diff_lng = diff.lng().degrees
	direction = (('N' if diff_lat >= 0 else 'S') if abs(diff_lat) > 1e-4 else '') + \
		(('E' if diff_lng >= 0 else 'W') if abs(diff_lng) > 1e-4 else '')
	return direction

#Returns an integer representing the distance between A and B	
def get_dist(ptA, ptB="default"):
	if ptB is "default":
		ptB = config.get("LOCATION")
	if ptB is None:
		return 0 #No location set
	latA = radians(ptA[0])
	lngA = radians(ptA[1])
	latB = radians(ptB[0])
	lngB = radians(ptB[1])
	dLat = latB - latA
	dLng = lngB - lngA
	
	a = sin(dLat / 2)**2 + cos(latA) * cos(latB) * sin(dLng / 2)**2
	c = 2 * atan2(sqrt(a), sqrt(1 - a))
	radius = 6373000 #radius of earth in meters
	if config['UNITS'] == 'imperial':
		radius = 6975175 #radius of earth in yards
	dist = c * radius
	return dist

#Return back the following:
#time_left = Time remaining in minutes and seconds
#time_12 = Dissapear time in 12h format, eg "2:30:16 PM"	
#time_24 = Dissapear time in 24h format including seconds, eg "14:30:16"
def get_timestamps(t):
	s = (t - datetime.utcnow()).total_seconds()
	(m, s) = divmod(s, 60)
	(h, m) = divmod(m, 60)
	d = timedelta(hours = h, minutes = m, seconds = s)
	if "TIMEZONE" in config:
		disappear_time = datetime.now(tz=config.get("TIMEZONE")) + d
	else:
		disappear_time = datetime.now() + d
	time_left = "%dm %ds" % (m, s)
	time_12 = disappear_time.strftime("%I:%M:%S") + disappear_time.strftime("%p").lower()
	time_24 = disappear_time.strftime("%H:%M:%S")
	return (time_left, time_12, time_24)
	
#########################################################################

###################### PARAMS THAT REQUIRE API_KEY ######################

#Returns the LAT,LNG of a location given by either a name or coordinates
def get_pos_by_name(location_name):
	prog = re.compile("^(\-?\d+\.\d+)[,\s]\s*(\-?\d+\.\d+?)$")
	res = prog.match(location_name)
	latitude, longitude = None, None
	if res:
		latitude, longitude = float(res.group(1)), float(res.group(2))
	elif location_name:
		if 'GMAPS_CLIENT' not in config: #Check if key was provided
			log.error("No Google Maps API key provided - unable to find location by name.")
			return None
		result = config['GMAPS_CLIENT'].geocode(location_name)
		loc = result[0]['geometry']['location']
		latitude, longitude = loc.get("lat"), loc.get("lng")
	log.info("Location found: %f,%f" % (latitude, longitude))
	return [latitude, longitude]
	
#Returns a static map url with <lat> and <lng> parameters for dynamic test
def get_static_map_url(settings):
	if not parse_boolean(settings.get('enabled', 'True')):
		return None
	width = settings.get('width', '250')
	height = settings.get('height', '125')
	maptype = settings.get('maptype', 'roadmap')
	zoom = settings.get('zoom', '15')

	center = '{},{}'.format('<lat>','<lng>')
	query_center = 'center={}'.format(center)
	query_markers =  'markers=color:red%7C{}'.format(center)
	query_size = 'size={}x{}'.format(width, height)
	query_zoom = 'zoom={}'.format(zoom)
	query_maptype = 'maptype={}'.format(maptype)
	
	map = ('https://maps.googleapis.com/maps/api/staticmap?' +
				query_center + '&' + query_markers + '&' +
				query_maptype + '&' + query_size + '&' + query_zoom)
	
	if 'API_KEY' in config:
		map = map + ('&key=%s' % config['API_KEY'])
		log.debug("API_KEY added to static map url.")
	log.debug("Static Map URL: " + map)
	return map

#Checks is a line contains any subsititions located in args
def contains_arg(line, args):
	for word in args:
		if ('<' + word + '>') in line:
			return True
	return False
	
#Returns true if string contains an argument that requires 
def set_optional_args(line):
	#Reverse Location
	args = { 'address', 'postal', 'neighborhood', 'sublocality', 'city', 'county', 'state', 'country' }
	config['REV_LOC'] = config['REV_LOC'] or contains_arg(line, args) 
	log.debug("REV_LOC set to %s" % config['REV_LOC'])
	
	#Walking Time
	args = {'walk_dist', 'walk_time'}
	config['DM_WALK'] = config['DM_WALK'] or contains_arg(line, args) 
	log.debug("DM_WALK set to %s" % config['DM_WALK'])
	
	#Biking Time
	args = {'bike_dist', 'bike_time'}
	config['DM_BIKE'] = config['DM_BIKE'] or contains_arg(line, args) 
	log.debug("DM_BIKE set to %s" % config['DM_BIKE'])
	
	#Driving Time
	args = {'drive_dist', 'drive_time'}
	config['DM_DRIVE'] = config['DM_DRIVE'] or contains_arg(line, args) 
	log.debug("DM_DRIVE set to %s" % config['DM_DRIVE'])
	
#Returns information on location based on info	
def reverse_location(info):
	if 'GMAPS_CLIENT' not in config: #Check if key was provided
			log.error("No Google Maps API key provided - unable to reverse geocode.")
			return {}
	lat, lng = info['lat'], info['lng']
	result = config['GMAPS_CLIENT'].reverse_geocode((lat,lng))[0]
	loc = {}
	for item in result['address_components']:
		for category in item['types']:
			loc[category] = item['short_name']
	details = {
		'address': "%s %s" % (loc.get('street_number'), loc.get('route'),),
		'postal': "%s" % (loc.get('postal_code')),
		'neighborhood': loc.get('neighborhood'),
		'sublocality': loc.get('sublocality'),
		'city': loc.get('locality', loc.get('postal_town')), #try postal town if no city
		'county': loc.get('administrative_area_level_2'),
		'state': loc.get('administrative_area_level_1'),
		'country': loc.get('country')
	}
	return details

# Returns a set with walking data and walking duration via Google Distance Matrix API
def get_walking_data(info):
	ptB = config.get("LOCATION")
	if ptB is None:
		log.error("No location has been set. Unable to get walking data.")
		return {}
	origin = "{},{}".format(info['lat'], info['lng'])
	dest = "{},{}".format(ptB[0], ptB[1])
	data = { 'walk_dist': "!error!", 'walk_time': "!error!" }
	try:
		result = config['GMAPS_CLIENT'].distance_matrix(origin, dest, mode='walking', units=config['UNITS'])
		result = result.get('rows')[0].get('elements')[0]
		data = {
			'walk_dist': result.get('distance').get('text').encode('utf-8'),
			'walk_time': result.get('duration').get('text').encode('utf-8'),
		}
	except Exception as e:
		log.error("Error geting walking data : %s" % e)
	return data;

# Returns a set with biking data and biking duration via Google Distance Matrix API
def get_biking_data(info):
	ptB = config.get("LOCATION")
	if ptB is None:
		log.error("No location has been set. Unable to get biking data.")
		return {}
	origin = "{},{}".format(info['lat'], info['lng'])
	dest = "{},{}".format(ptB[0], ptB[1])
	data = { 'bike_dist': "!error!", 'bike_time': "!error!" }
	try:
		result = config['GMAPS_CLIENT'].distance_matrix(origin, dest, mode='bicycling', units=config['UNITS'])
		result = result.get('rows')[0].get('elements')[0]
		data = {
			'bike_dist': result.get('distance').get('text').encode('utf-8'),
			'bike_time': result.get('duration').get('text').encode('utf-8'),
		}
	except Exception as e:
		log.error("Error geting biking data : %s" % e)
	return data;
	
# Returns a set with biking data and biking duration via Google Distance Matrix API
def get_driving_data(info):
	ptB = config.get("LOCATION")
	if ptB is None:
		log.error("No location has been set. Unable to get biking data.")
		return {}
	origin = "{},{}".format(info['lat'], info['lng'])
	dest = "{},{}".format(ptB[0], ptB[1])
	data = { 'drive_dist': "!error!", 'drive_time': "!error!" }
	try:
		result = config['GMAPS_CLIENT'].distance_matrix(origin, dest, mode='driving', units=config['UNITS'])
		result = result.get('rows')[0].get('elements')[0]
		data = {
			'drive_dist': result.get('distance').get('text').encode('utf-8'),
			'drive_time': result.get('duration').get('text').encode('utf-8'),
		}
	except Exception as e:
		log.error("Error geting biking data : %s" % e)
	return data;
#####################################################################



#Logging
import logging
log = logging.getLogger(__name__)

#Python Utility imports
import os
import json
import configargparse
import time
import geocoder
import sys
import re
from glob import glob
from datetime import datetime, timedelta
from math import radians, sin, cos, atan2, sqrt
from s2sphere import LatLng
import urllib
import yaml

#Local imports
from . import config
from geofence import Geofence

def parse_unicode(bytestring):
    decoded_string = bytestring.decode(sys.getfilesystemencoding())
    return decoded_string
	
def parse_boolean(val):
	b = val.lower()
	if b in {'t', 'true', 'y', 'yes'}:
		return True
	return False
	
def set_config(root_path):
	parser = configargparse.ArgParser()
	parser.add_argument('-H', '--host', help='Set web server listening host', default='127.0.0.1')
	parser.add_argument('-P', '--port', type=int, help='Set web server listening port', default=4000)
	parser.add_argument('-l', '--location', type=parse_unicode, help='Location, can be an address or coordinates')
	parser.add_argument('-L', '--locale', help='Locale for Pokemon names: default en, check locale folder for more options', default='en')
	parser.add_argument('-d', '--debug', help='Debug Mode', action='store_true')
	parser.add_argument('-gf', '--geofence', help='Specify a file of coordinates, limiting alerts to within this area')
	parser.set_defaults(DEBUG=False)
	
	args = parser.parse_args()
	
	config['ROOT_PATH'] = root_path
	config['HOST'] = args.host
	config['PORT'] = args.port
	config['LOCALE'] = args.locale
	config['DEBUG'] = args.debug
	
	if args.location:
		config['LOCATION'] =  get_pos_by_name(args.location)
	
	if args.geofence:
		config['GEOFENCE'] = Geofence(os.path.join(root_path, args.geofence))
	
	return config

#Parse notify list
def make_notify_list(want_list):
	notify = {}
	for name in want_list:
		id = get_pkmn_id(name)
		if parse_boolean(want_list[name]) :
			notify[id] = float('inf')
		else:
			try:
				notify[id] = float(want_list[name])
			except ValueError:
				continue
	return notify
	
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

#Returns a String representing the nearest address to a lng, lat	
def get_nearest_location(lat, lng):
	return geocoder.google([lat,lng], method='reverse')
	 

#Returns a String link to Google Maps Pin at the location	
def get_gmaps_link(lat, lng):
	latLon = '{},{}'.format(repr(lat), repr(lng))
	return 'http://maps.google.com/maps?q={}'.format(latLon)
		

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

#Returns an integer representing the distance between A and B in meters	
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
	dist = c * 6373000 #radius of earth in meters
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
	disappear_time = datetime.now() + d
	time_left = "%dm %ds" % (m, s)
	time_12 = disappear_time.strftime("%I:%M") + disappear_time.strftime("%p").lower()
	time_24 = disappear_time.strftime("%H:%M:%S")
	return (time_left, time_12, time_24)
	
#Return a version of the string with the correct substitutions made	
def replace(string, pkinfo):
	s = string.encode('utf-8')
	for key in pkinfo:
		s = s.replace("<{}>".format(key), pkinfo[key])
	return s

#Get the latitude and longiture of a Place	
def get_pos_by_name(location_name):
	prog = re.compile("^(\-?\d+\.\d+)[,\s]\s*(\-?\d+\.\d+?)$")
	res = prog.match(location_name)
	latitude, longitude = None, None
	if res:
		latitude, longitude = float(res.group(1)), float(res.group(2))
	elif location_name:
		loc = geocoder.google(location_name)
		log.info(loc)
		if loc:
			latitude, longitude = loc.lat, loc.lng

	return [latitude, longitude]

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

#Returns a string containing travel time in travel mode specified
def get_travel_time(ptA,  mode, ptB="default"):
	if ptB is "default":
	        ptB = config.get("LOCATION")
	if ptB is None:
	        return 0 #No location set
	ptaA = [42.028632, -87.788187]
	ptB = [42.024679, -87.769819]
	url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins=%s,%s&destinations=%s,%s&mode=%s&units=imperial" % (ptA[0], ptA[1], ptB[0], ptB[1], mode)
	response = urllib.urlopen(url)
	data = yaml.safe_load(response.read())
	if (data.get("rows")[0].get("elements")[0].get("status") != "OK"):
			log.debug("Travel time is returning no results for " + mode)
			return 0
	return parse_duration(data.get("rows")[0].get("elements")[0].get("duration").get("text"))

def parse_duration (duration):
	regex = re.compile(r'((?P<days>\d+?) days?)? ?((?P<hours>\d+?) hours?)? ?((?P<minutes>\d+?) mins?)?')
	parts = regex.match(duration)
	partsdict = parts.groupdict()
	durationstring = ""
	if partsdict['days'] != None:
		durationstring += partsdict['days'] + "day "
	if partsdict['hours'] != None:
		durationstring += partsdict['hours'] + "hr "
	if partsdict['minutes'] != None:
		durationstring += partsdict['minutes'] + "min "
	return durationstring

#Used for lazy installs - installs required module with pip
def pip_install(module, version):
	import pip
	import subprocess
	target = "{}=={}".format(module, version)
	log.info("Attempting to pip install %s..." % target)
	subprocess.call(['pip', 'install', target])
	log.info("%s install complete." % target)

#Server imports
from gevent import monkey; monkey.patch_all()
from flask import Flask, request, abort
from gevent import wsgi

#Set up logging
import logging
logging.basicConfig(format='%(asctime)s [%(module)18s] [%(levelname)7s] %(message)s', level=logging.INFO)
log = logging.getLogger()

#Python Modules
import sys
import json
import os

#Local Modules
from alarms import config, set_config
from alarms.alarm_manager import Alarm_Manager
from alarms.utils import get_pos_by_name
from alarms.geofence import get_geofence_static_map

reload(sys)
sys.setdefaultencoding('utf8')

#Intialize globals
app = Flask(__name__)
alarm_thread = None


@app.route('/',methods=['POST'])
def trigger_alert():
	log.debug("POST request received from %s." % (request.remote_addr))
	data = json.loads(request.data)
	id = get_id(data)
	alarm_thread.update(id, data)
	return "OK"
	
def get_id(data):
	if data['type'] == 'pokemon':
		return data.get('encounter_id')
	elif data['type'] == 'pokestop':
		return data.get('pokestop_id')
	elif data['type'] == 'gym':
		return data.get('gym_id')
	elif data['type'] == 'gym-details':
		return data.get('id')
	else:
		return None
	
@app.route('/location/',methods=['GET'])
def return_location():
	return "Current location is %s" % config.get('LOCATION')
	
@app.route('/location/',methods=['POST'])
def update_location():
	try:
		config['LOCATION'] = get_pos_by_name(request.args.get('location'))
	except Exception as e:
		log.error("Error changing location: %s" % e)
		abort(400)
	log.info("Location updated via POST request!")
	return "Location changed to : %s" % config['LOCATION']

@app.route('/geofence/',methods=['GET'])
def return_geofence():
	geofence_url = get_geofence_static_map()
	if geofence_url != False:
		return '<img src="{}">'.format(geofence_url)
	else:
		return 'No location or geofence set'

if __name__ == '__main__':
	#Standard Logging
	log.setLevel(logging.INFO)
	logging.getLogger('alarms').setLevel(logging.INFO)
	logging.getLogger('requests').setLevel(logging.WARNING)
	logging.getLogger('pywsgi').setLevel(logging.WARNING)
	logging.getLogger('connectionpool').setLevel(logging.WARNING)
	
	#Parse arguments and set up config
	config = set_config(os.path.abspath(os.path.dirname(__file__)))
	
	#Debug options
	if config['DEBUG']:
		log.info("Debug mode activated!")
		log.setLevel(logging.DEBUG)
		logging.getLogger('alarms').setLevel(logging.DEBUG)
		logging.getLogger('flask').setLevel(logging.DEBUG)
		logging.getLogger('pywsgi').setLevel(logging.DEBUG)
		logging.getLogger('requests').setLevel(logging.DEBUG)

	#Start up Alarm_Manager
	alarm_thread = Alarm_Manager()
	alarm_thread.start()
	
	#Start up Server
	log.info("Webhook server running on http://%s:%s" % (config['HOST'], config['PORT']))
	server = wsgi.WSGIServer((config['HOST'], config['PORT']), app, log=logging.getLogger('pywsgi'))
	server.serve_forever()
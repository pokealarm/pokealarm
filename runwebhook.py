#Server imports
from gevent import monkey; monkey.patch_all()
from flask import Flask, request
from gevent import wsgi

#Set up logging
import logging
logging.basicConfig(format='%(asctime)s [%(module)18s] [%(levelname)7s] %(message)s', level=logging.INFO)
log = logging.getLogger()

#Python Modules
import sys
import json
import os
import Queue
import re

#Local Modules
from alarms import config, set_config
from alarms.alarm_manager import Alarm_Manager

reload(sys)
sys.setdefaultencoding('utf8')

#Intialize globals
app = Flask(__name__)
data_queue = Queue.Queue()


@app.route('/',methods=['POST'])
def trigger_alert():
	log.debug("POST request received from %s." % (request.remote_addr))
	data = json.loads(request.data)
	data_queue.put(data)
	return ""

@app.route('/location/')
def get_location():
	if 'LOCATION' in config:
		return "%s,%s" % (config['LOCATION'][0], config['LOCATION'][1])
	else:
		return "No location configured"

@app.route('/location/<string:new_loc_str>')
def change_location(new_loc_str):
	loc_match = re.match('^([-]?(?:[1-8]?\d(?:\.\d+)?|90(?:\.0+))),\s*([-]?(?:180(?:\.0+)?|(?:(?:1[0-7]\d)|(?:[1-9]?\d))(?:\.\d+)?))$', new_loc_str) # Validate coordinate input
	if loc_match is None:
		return "Invalid location formatting"
	config['LOCATION'] = [loc_match.group(1), loc_match.group(2)]
	return "Location set: %s,%s" % (loc_match.group(1), loc_match.group(2)) 

if __name__ == '__main__':
	#Parse arguments and set up config
	config = set_config(os.path.abspath(os.path.dirname(__file__)))
	
	#Debug options
	if config['DEBUG']:
		log.info("Debug mode activated!")
		log.setLevel(logging.DEBUG)
		logging.getLogger('requests').setLevel(logging.DEBUG)
		logging.getLogger('flask').setLevel(logging.DEBUG)
		logging.getLogger('pywsgi').setLevel(logging.DEBUG)
	else:
		log.setLevel(logging.INFO)
		logging.getLogger('requests').setLevel(logging.WARNING)
		logging.getLogger('alarms').setLevel(logging.INFO)
		logging.getLogger('pywsgi').setLevel(logging.WARNING)
	
	#Start up Alarm_Manager
	alarm_thread = Alarm_Manager(data_queue)
	alarm_thread.start()
	
	#Start up Server
	log.info("Webhook server running on http://%s:%s" % (config['HOST'], config['PORT']))
	server = wsgi.WSGIServer((config['HOST'], config['PORT']), app, log=logging.getLogger('pywsgi'))
	server.serve_forever()
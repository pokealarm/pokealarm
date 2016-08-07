#Server imports
from gevent import monkey; monkey.patch_all()
from flask import Flask, request
from gevent import wsgi

#Python Utility imports
import sys
import json
import logging
import os
import Queue

#Local imports
from alarms import config
from alarms import set_config
from alarms.alarm_manager import Alarm_Manager

#Set up logging
logging.basicConfig(format='%(asctime)s [%(module)18s] [%(levelname)7s] %(message)s', level=logging.INFO)
log = logging.getLogger()
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
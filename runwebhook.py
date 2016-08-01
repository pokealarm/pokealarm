#Server imports
from gevent import monkey
monkey.patch_all()
from flask import Flask, request
from gevent import wsgi

#Python Utility imports
import json
import logging
import os
from Queue import Queue

#Local imports
from alarms import config
from alarms.utilities import set_config
from alarms.alarm_manager import Alarm_Manager

#Set up logging
logging.basicConfig(format='%(asctime)s [%(module)14s] [%(levelname)7s] %(message)s', level=logging.INFO)
log = logging.getLogger()

#Intialize globals
app = Flask(__name__)
data_queue = Queue()


@app.route('/',methods=['POST'])
def trigger_alert():
	data = json.loads(request.data)
	data_queue.put(data)
	return ""

if __name__ == '__main__':
	config = set_config(os.path.abspath(os.path.dirname(__file__)))
	
	if config['DEBUG']:
		logging.basicConfig(level=logging.DEBUG)
	else :
		logging.getLogger('werkzeug').setLevel(logging.ERROR)
		logging.getLogger('requests').setLevel(logging.DEBUG)
		logging.getLogger('alarms').setLevel(logging.INFO)

	alarm_thread = Alarm_Manager(data_queue)
	alarm_thread.start()
	
	log.info("Webhook server running on http://%s:%s" % (config['HOST'], config['PORT']))
	server = wsgi.WSGIServer((config['HOST'], config['PORT']), app)
	server.serve_forever()
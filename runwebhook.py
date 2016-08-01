import json
import logging
import os

from flask import Flask, request
from Queue import Queue
from threading import Thread

from alarms import config
from alarms.alarm_manager import Alarm_Manager
from alarms.utilities import set_config

logging.basicConfig(format='%(asctime)s [%(module)14s] [%(levelname)7s] %(message)s', level=logging.INFO)
log = logging.getLogger()

app = Flask(__name__)
queue = Queue()

class Worker(Thread):
	def __init__(self, queue):
		super(Worker, self).__init__()
		self.queue = queue
		self.alerts = Alarm_Manager()

	def run(self):
		while True:
			pkmn = self.queue.get(block=True, timeout=None)
			self.alerts.trigger_pkmn(pkmn)

@app.route('/',methods=['POST'])
def trigger_alert():
	log.debug("POST request response has been triggered.")
	data = json.loads(request.data)
	if data['type'] == 'pokemon' :
		log.debug("POST request is  a pokemon.")
		pkmn = data['message']
		queue.put(pkmn)
	elif data['type'] == 'pokestop' : 
		log.debug("Pokestop notifications not yet implimented.")
		#do nothing
	elif data['type'] == 'pokegym' :
		log.debug("Pokegym notifications not yet implimented.")
		#do nothing
	return ""

if __name__ == '__main__':
	config = set_config(os.path.abspath(os.path.dirname(__file__)))
	if config['DEBUG']:
		logging.basicConfig(level=logging.DEBUG)
	else :
		logging.getLogger('werkzeug').setLevel(logging.ERROR)
		logging.getLogger('requests').setLevel(logging.DEBUG)
		logging.getLogger('alarms').setLevel(logging.INFO)
		logging.getLogger('alarms').setLevel(logging.INFO)

	worker = Worker(queue)
	worker.daemon = True
	worker.start()

	
	app.run(debug=config['DEBUG'],host=config['HOST'], port=config['PORT'])
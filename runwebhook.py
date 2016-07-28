import json
import logging
import os

from flask import Flask, request

from alarms import config
from alarms.alarm_manager import Alarm_Manager
from alarms.utilities import get_args

logging.basicConfig(format='%(asctime)s [%(module)14s] [%(levelname)7s] %(message)s')
log = logging.getLogger()

app = Flask(__name__)
alerts = Alarm_Manager()

@app.route('/',methods=['POST'])
def trigger_alert():
	log.debug("POST request response has been triggered.")
	data = json.loads(request.data)
	if data['type'] == 'pokemon' :
		pkmn = data['message']
		log.debug('message')
		alerts.trigger_pkmn(pkmn)			
	elif data['type'] == 'pokestop' : 
		log.debug("Pokestop notifications not yet implimented.")
		#do nothing
	elif data['type'] == 'pokegym' :
		log.debug("Pokegym notifications not yet implimented.")
		#do nothing
	return "OK"
	
if __name__ == '__main__':
	#config['ROOT_PATH'] = os.path.join(os.path.dirname(__file__))
	log.setLevel(logging.DEBUG);
	
	log.info("App started")
	app.run()
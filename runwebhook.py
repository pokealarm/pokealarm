import json
import logging
import os

from flask import Flask, request

from alarms import config
from alarms.alarm_manager import Alarm_Manager
from alarms.utilities import set_config

logging.basicConfig(format='%(asctime)s [%(module)14s] [%(levelname)7s] %(message)s')
log = logging.getLogger()

app = Flask(__name__)
alerts = Alarm_Manager()

@app.route('/',methods=['POST'])
def trigger_alert():
	log.debug("POST request response has been triggered.")
	data = json.loads(request.data)
	if data['type'] == 'pokemon' :
		log.debug("POST request is  a pokemon.")
		pkmn = data['message']
		alerts.trigger_pkmn(pkmn)			
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
		log.setLevel(logging.DEBUG)
		logging.getLogger("alarms.utilities").setLevel(logging.DEBUG)
		logging.getLogger("alarms.alarm_managers").setLevel(logging.DEBUG)
	else :
		logging.getLogger("requests").setLevel(logging.WARNING)
		logging.getLogger('werkzeug').setLevel(logging.ERROR)
		logging.getLogger("alarms").setLevel(logging.INFO)
	
	app.run(debug=config['DEBUG'],host=config['HOST'], port=config['PORT'])
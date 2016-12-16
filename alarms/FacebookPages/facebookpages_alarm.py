#Setup logging
import logging
log = logging.getLogger(__name__)

#Python Modules
from datetime import datetime

#Local Modules
from ..alarm import Alarm
from ..utils import *

#Exernal Modules
import facebook

class FacebookPages_Alarm(Alarm):

	_defaults = {
		'pokemon':{
			'message': "A wild <pkmn> has appeared! Available until <24h_time> (<time_left>).",
			'location': "True"
		},
		'pokestop':{
			'message': "Someone has placed a lure on a Pokestop! Lure will expire at <24h_time> (<time_left>).",
			'location': "True"
		},
		'gym':{
			'message':"A Team <old_team> gym has fallen! It is now controlled by <new_team>.",
			'location': "True"
		}
	}

	#Gather settings and create alarm
	def __init__(self, settings):
		#Service Info
		self.page_access_token = settings['page_access_token']
		self.startup_message = settings.get('startup_message', "True")
		self.startup_list = settings.get('startup_list', "True")
				
		#Set Alerts
		self.pokemon = self.set_alert(settings.get('pokemon', {}), self._defaults['pokemon'])
		self.pokestop = self.set_alert(settings.get('pokestop', {}), self._defaults['pokestop'])
		self.gym = self.set_alert(settings.get('gyms', {}), self._defaults['gym'])
		
		#Connect and send startup messages
		self.connect()
		timestamps = get_timestamps(datetime.utcnow());
		if parse_boolean(self.startup_message):
			self.client.put_wall_post(message="%s - PokeAlarm has intialized!" % timestamps[2])
		log.info("FacebookPages Alarm intialized.")
		
	#Establish connection with FacebookPages
	def connect(self):
		self.client = facebook.GraphAPI(self.page_access_token)
			
	#Set the appropriate settings for each alert
	def set_alert(self, settings, default):
		alert = {}
		alert['message'] = settings.get('message', default['message'])
		
		if parse_boolean(settings.get('location', default['location'])):
			alert['attachment'] = { 'link': "<gmaps>" }
			
		return alert
	
	#Post Pokemon Message
	def send_alert(self, alert, info):
		args = { "message": replace(alert['message'], info) }
		
		if alert['attachment']:
			args['attachment'] = {
				"link": replace(alert['attachment']['link'], info)
			}		
		
		try_sending(log, self.connect, "FacebookPages", self.client.put_wall_post, args)
		
	#Trigger an alert based on Pokemon info
	def pokemon_alert(self, pokemon_info):
		self.send_alert(self.pokemon, pokemon_info)
	
	#Trigger an alert based on Pokestop info
	def pokestop_alert(self, pokestop_info):
		self.send_alert(self.pokestop, pokestop_info)
		
	#Trigger an alert based on Gym info
	def gym_alert(self, gym_info):
		self.send_alert(self.gym, gym_info)
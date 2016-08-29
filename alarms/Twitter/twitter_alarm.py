#Setup logging
import logging
log = logging.getLogger(__name__)

#Python Modules
from datetime import datetime

#Local Modules
from ..alarm import Alarm
from ..utils import *

#Exernal Modules
from twitter import Twitter, OAuth

class Twitter_Alarm(Alarm):

	_defaults = {
		'pokemon':{
			'status': "A wild <pkmn> has appeared! Available until <24h_time> (<time_left>). <gmaps>",
		},
		'pokestop':{
			'status': "Someone has placed a lure on a Pokestop! Lure will expire at <24h_time> (<time_left>).  <gmaps>",
		}
	}

	#Gather settings and create alarm
	def __init__(self, settings):
		#Service Info
		self.token = settings['access_token']
		self.token_key = settings['access_secret']
		self.con_secret = settings['consumer_key']
		self.con_secret_key = settings['consumer_secret']
		self.startup_message = settings.get('startup_message', "True")
				
		#Set Alerts
		self.pokemon = self.set_alert(settings.get('pokemon', {}), self._defaults['pokemon'])
		self.pokestop = self.set_alert(settings.get('pokestop', {}), self._defaults['pokestop'])
				
		#Connect and send startup message
		self.connect()
		if parse_boolean(self.startup_message):
			self.client.statuses.update(status="%s: PokeAlarm has intialized!" % datetime.now().strftime("%H:%M:%S"))
		log.info("Twitter Alarm intialized.")
		
	#Establish connection with Twitter
	def connect(self):
		self.client = Twitter(
			auth=OAuth(self.token, self.token_key, self.con_secret, self.con_secret_key))
			
	#Set the appropriate settings for each alert
	def set_alert(self, settings, default):
		alert = {}
		alert['status'] = settings.get('status', default['status'])
		return alert
	
	#Post Pokemon Status
	def send_alert(self, alert, info):
		args = { "status": replace(alert['status'], info)}
		try_sending(log, self.connect, "Twitter", self.client.statuses.update, args)
		
	#Trigger an alert based on Pokemon info
	def pokemon_alert(self, pokemon_info):
		self.send_alert(self.pokemon, pokemon_info)
	
	#Trigger an alert based on Pokestop info
	def pokestop_alert(self, pokestop_info):
		self.send_alert(self.pokestop, pokestop_info)
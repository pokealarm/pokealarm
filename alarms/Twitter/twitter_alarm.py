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
			'status': "<pkmn> <iv>% (<atk>/<dfs>/<sta>/<move1>/<move2>) till <24h_time> (<time_left>). <gmaps>",
		},
		'pokestop':{
			'status': "Someone has placed a lure on a Pokestop! Lure will expire at <24h_time> (<time_left>).  <gmaps>",
		},
		'gym':{
			'status':"A Team <old_team> gym has fallen! It is now controlled by <new_team>. <gmaps>"
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
		self.startup_list = settings.get('startup_list', "True")
				
		#Set Alerts
		self.pokemon = self.set_alert(settings.get('pokemon', {}), self._defaults['pokemon'])
		self.pokestop = self.set_alert(settings.get('pokestop', {}), self._defaults['pokestop'])
		self.gym = self.set_alert(settings.get('gyms', {}), self._defaults['gym'])
		
		#Connect and send startup messages
		self.connect()
		timestamps = get_timestamps(datetime.utcnow());
		if parse_boolean(self.startup_message):
			self.client.statuses.update(status="%s - PokeAlarm has intialized!" % timestamps[2])
		if parse_boolean(self.startup_list):
			for line in notify_list_multi_msgs(config["NOTIFY_LIST"],140, "We will tweet about the following pokemon", timestamps[2]):
				self.client.statuses.update(status="%s" % line)
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
		
	#Trigger an alert based on Gym info
	def gym_alert(self, gym_info):
		self.send_alert(self.gym, gym_info)
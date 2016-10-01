#Setup Logging
import logging
log = logging.getLogger(__name__)

#Python modules
import httplib
import urllib

#Local modules
from ..alarm import Alarm
from ..utils import *

#External modules

class Pushover_Alarm(Alarm):
	
	_defaults = {
		'pokemon':{
			'title':"A wild <pkmn> has appeared!",
			'url':"<gmaps>",
			'url_title':"Google Maps Link",
			'message':"Available until <24h_time> (<time_left>)."
		},
		'pokestop':{
			'title':"Someone has placed a lure on a Pokestop!",
			'url':"<gmaps>",
			'url_title':"Google Maps Link",
			'message':"Lure will expire at <24h_time> (<time_left>)."
		},
		'gym':{
			'title':"A Team <old_team> gym has fallen!",
			'url':"<gmaps>",
			'url_title':"Google Maps Link",
			'message':"It is now controlled by <new_team>."
		}
	}
	
	#Gather settings and create alarm
	def __init__(self, settings):
		#Service Info
		self.app_token = settings['app_token']
		self.user_key = settings['user_key']
		self.startup_message = settings.get('startup_message', "True")
		self.startup_list = settings.get('startup_list', "True")
		self.sound = settings.get('sound')
		self.def_pkmn_sound = settings.get('default_pkmn_sound')
		#Set Alerts
		self.pokemon = self.set_alert(settings.get('pokemon', {}), self._defaults['pokemon'])
		self.pokestop = self.set_alert(settings.get('pokestop', {}), self._defaults['pokestop'])
		self.gym = self.set_alert(settings.get('gyms', {}), self._defaults['gym'])
		
		#Connect and send startup messages
		if parse_boolean(self.startup_message):
		    self.send_pushover("PokeAlarm has been activated! We will alert this channel about pokemon.", sound = self.sound)
		log.info("Pushover Alarm intialized")
		
	#(Re)establishes Pushover connection
	def connect(self):
		#Empty - no reconnect needed
		pass
	
	#Set the appropriate settings for each alert
	def set_alert(self, settings, default):
		alert = {}
		alert['title'] = settings.get('title', default['title'])
		alert['url'] = settings.get('url', default['url'])
		alert['url_title'] = settings.get('url_title', default['url_title'])
		alert['message'] = settings.get('message', default['message'])
		alert['sound'] = settings.get('sound', self.sound)
		alert['def_pkmn_sound'] = settings.get('default_pkmn_sound', self.def_pkmn_sound)
		return alert
		
	#Send Alert to the Pushover
	def send_alert(self, alert, info):
		#If the pokemon has no specific sound set we use the default_pokemon_sound when this variable is also set
		if replace(alert['sound'], info) == 'None' and alert['def_pkmn_sound'] != None:
			alert['sound'] = alert['def_pkmn_sound']
		args  = {
			'message': replace(alert['message'], info),
			'title': replace(alert['title'], info),
			'url': replace(alert['url'], info),
			'url_title': replace(alert['url_title'], info),
			'sound': replace(alert['sound'], info)
		}
		try_sending(log, self.connect, "Pushover",  self.send_pushover, args)
	
	#Trigger an alert based on Pokemon info
	def pokemon_alert(self, pokemon_info):
		self.send_alert(self.pokemon, pokemon_info)
	
	#Trigger an alert based on Pokestop info
	def pokestop_alert(self, pokestop_info):
		self.send_alert(self.pokestop, pokestop_info)
	
	#Trigger an alert based on Pokestop info
	def gym_alert(self, gym_info):
		self.send_alert(self.gym, gym_info)
			
	#Generic send pushover
	def send_pushover(self, message, title='PokeAlert', url=None, url_title=None, sound=None):
		#Establish connection
		connection = httplib.HTTPSConnection("api.pushover.net:443", timeout=10)
		payload = {"token": self.app_token, 
				"user": self.user_key, 
				"title": title,
				"message": message}	
		if url is not None:
			payload['url'] = url
			payload['url_title'] = url_title
		if sound is not None:
			payload['sound'] = sound
		connection.request("POST", "/1/messages.json", urllib.urlencode(payload), 
			{"Content-Type": "application/x-www-form-urlencoded"})
		r = connection.getresponse()
		if r.status != 200:
			raise httplib.HTTPException("Response not 200")

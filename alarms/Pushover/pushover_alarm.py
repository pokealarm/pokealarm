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
		}
	}
	
	#Gather settings and create alarm
	def __init__(self, settings):
		#Service Info
		self.app_token = settings['app_token']
		self.user_key = settings['user_key']
		#Set Alerts
		self.pokemon = self.set_alert(settings.get('pokemon', {}), self._defaults['pokemon'])
		#Connect and send startup message
		self.startup_message = settings.get('startup_message', "True")
		log.info("Pushover Alarm intialized")
		if parse_boolean(self.startup_message):
		    self.send_pushover("PokeAlarm has been activated! We will alert this channel about pokemon.")
	
	#Generic send pushover
	def send_pushover(self, message, title='PokeAlert', url=None, url_title=None):
		##Establish connection
		connection = httplib.HTTPSConnection("api.pushover.net:443", timeout=10)
		payload = {"token": self.app_token, 
				"user": self.user_key, 
				"title": title,
				"message": message}	
		if url is not None:
			payload['url'] = url
			payload['url_title'] = url_title
		connection.request("POST", "/1/messages.json", urllib.urlencode(payload), 
			{"Content-Type": "application/x-www-form-urlencoded"})
		r = connection.getresponse()
		if r.status != 200:
			raise httplib.HTTPException("Response not 200")
	
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
		return alert
	
	#Trigger an alert based on Pokemon info
	def pokemon_alert(self, pokemon_info):
		self.send_alert(self.pokemon, pokemon_info)
	
	#Send Alert to the Pushbullet
	def send_alert(self, alert, info):
		args  = {
			'message': replace(alert['message'], info),
			'title': replace(alert['title'], info),
			'url': replace(alert['url'], info),
			'url_title': replace(alert['url_title'], info)
		}
		try_sending(log, self.connect, "Pushover",  self.send_pushover, args)
	

		

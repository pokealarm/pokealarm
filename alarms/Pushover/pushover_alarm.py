#Setup Logging
import logging
log = logging.getLogger(__name__)

#Python modules
import httplib
import urllib

#Local modules
from ..alarm import Alarm
from ..utils import *


class Pushover_Alarm(Alarm):
	
	#Gather settings and create alarm
	def __init__(self, settings):
		self.app_token = settings['app_token']
		self.user_key = settings['user_key']
		self.title = settings.get('title', 
			"A wild <pkmn> has appeared!")
		self.url = settings.get('url', 
			"<gmaps>")
		self.url_title = settings.get('url', 
			"Google Maps Link")
		self.message = settings.get('message', 
			"Available until <24h_time> (<time_left>).")
		log.info("Pushover Alarm intialized")
		self.send_pushover("PokeAlarm has been activated! We will text this account about pokemon.")
	
	#Empty - no reconnect needed
	def connect(self):
		pass
	
	#Send pokemon alert to pushover	
	def pokemon_alert(self, pkinfo):
		args  = {
			'message': replace(self.message, pkinfo),
			'title': replace(self.title, pkinfo),
			'url': replace(self.url, pkinfo),
			'url_title': replace(self.url_title, pkinfo)
		}
		try_sending(log, self.connect, "Pushover",  self.send_pushover, args)
	
	#Generic send pushover
	def send_pushover(self, message, title='PokeAlert', url=None, url_title="URL"):
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
		

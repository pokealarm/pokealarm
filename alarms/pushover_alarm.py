import logging

import httplib, urllib
from alarm import Alarm
from utils import *

log = logging.getLogger(__name__)

class Pushover_Alarm(Alarm):
	
	def __init__(self, settings):
		self.app_token = settings['app_token']
		self.user_key = settings['user_key']
		self.message = settings.get('message', 
			"A wild <pkmn> has appeared! Available until <24h_time> (<time_left>).")
		log.info("Pushover Alarm intialized")
		self.send_pushover("PokeAlarm has been activated! We will text this account about pokemon.")
		
	def pokemon_alert(self, pkinfo):
		message = replace(self.message, pkinfo)
		self.send_pushover(message, pkinfo)
		
	def send_pushover(self, msg, pkinfo=None):
		connection = httplib.HTTPSConnection("api.pushover.net:443")
		payload = {"token": self.app_token, 
				"user": self.user_key, 
				"title": "PokeAlert",
				"message": msg}
		
		if pkinfo is not None:
			payload['url'] = pkinfo['gmaps']
			payload['url_title'] = "GMaps-Link"
		
		connection.request("POST", "/1/messages.json", urllib.urlencode(payload), 
			{"Content-Type": "application/x-www-form-urlencoded"})
		connection.getresponse()

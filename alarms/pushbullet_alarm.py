import logging

from alarm import Alarm
from pushbullet import PushBullet

log = logging.getLogger(__name__)

class Pushbullet_Alarm(Alarm):
	
	def __init__(self, settings):
		self.client = PushBullet(settings['api_key']) 
		log_msg = "Pushbullet Alarm intialized"
		if 'name' in settings:
			self.name = settings['name']
			log_msg = log_msg + ":" + self.name
		log.info(log_msg)
		push = self.client.push_note("PokeAlarm activated!", "We will alert you about pokemon.")
		
	def pokemon_alert(self, pkinfo):
		notification_text = pkinfo['alert']
		if self.name :
			notification_text = self.name + ": " + notification_text
		gmaps_link = pkinfo['gmaps_link']
		time_text =  pkinfo['time_text']
		push = self.client.push_link(notification_text, google_maps_link, body=time_text)
	
import logging

from alarm import Alarm
from slacker import Slacker

log = logging.getLogger(__name__)

class Slack_Alarm(Alarm):
	
	def __init__(self, settings):
		self.client = Slacker(settings['api_key']) 
		self.channel = settings['channel']
		log_msg = "Slack Alarm intialized"
		if 'name' in settings:
			self.name = settings['name']
			log_mst = log_msg + ": " + self.name
		log.info(log_msg)
		self.client.chat.post_message(self.channel, 'PokeAlarm activated! We will alert this channel about pokemon.')
		
	def pokemon_alert(self, pkinfo):
		notification_text = pkinfo['alert']
		if hasattr(self, 'name') :
			notification_text = self.name + ": " + notification_text
		gmaps_link = pkinfo['gmaps_link']
		time_text =  pkinfo['time_text']
		self.client.chat.post_message(self.channel, notification_text + " " + time_text + " " + gmaps_link)
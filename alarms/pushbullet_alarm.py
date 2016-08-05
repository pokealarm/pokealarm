import logging

from alarm import Alarm
from pushbullet import PushBullet
from utils import *

log = logging.getLogger(__name__)

class Pushbullet_Alarm(Alarm):
	
	def __init__(self, settings):
		self.client = PushBullet(settings['api_key']) 
		self.sender = self.get_sender(self.client, settings.get('channel'))
		self.notify_text = settings.get('notify_text', "A wild <pkmn> has appeared!")
		self.link = settings.get('link', "<gmaps>")
		self.body_text = settings.get('body_text', "Available until <24h_time> (<time_left>).")
		log.info("Pushbullet Alarm intialized")
		push = self.sender.push_note("PokeAlarm activated!", "We will alert you about pokemon.")
		
	def pokemon_alert(self, pkinfo):
		notify_text = replace(self.notify_text, pkinfo)
		link = replace(self.link, pkinfo)
		body_text =  replace(self.body_text, pkinfo)
		push = self.sender.push_link(notify_text, link, body=body_text)
	
	#Attempt to get the channel, otherwise default to all devices
	def get_sender(self, client, channel_tag):
		req_channel = next((channel for channel in client.channels if channel.channel_tag == channel_tag), self.client)
		if req_channel is self.client and channel_tag is not None:
			log.error("Unable to find channel... Pushing to all devices instead...")
		else:
			log.info("Pushing to channel %s." % channel_tag)
		return req_channel
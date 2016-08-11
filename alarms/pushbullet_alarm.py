import logging

from alarm import Alarm
from pushbullet import PushBullet
from utils import *

log = logging.getLogger(__name__)

class Pushbullet_Alarm(Alarm):
	
	def __init__(self, settings):
		self.api_key = settings['api_key']
		self.channel = settings.get('channel')
		self.connect()
		self.title = settings.get('title', "A wild <pkmn> has appeared!")
		self.url = settings.get('url', "<gmaps>")
		self.body = settings.get('body', "Available until <24h_time> (<time_left>).")
		log.info("Pushbullet Alarm intialized")
		push = self.sender.push_note("PokeAlarm activated!", "We will alert you about pokemon.")
	
	#(Re)establishes Pushbullet connection
	def connect(self):
		self.client = PushBullet(self.api_key)
		self.sender = self.get_sender(self.client, self.channel)
		
	#Attempt to get the channel, otherwise default to all devices
	def get_sender(self, client, channel_tag):
		req_channel = next((channel for channel in client.channels if channel.channel_tag == channel_tag), self.client)
		if req_channel is self.client and channel_tag is not None:
			log.error("Unable to find channel... Pushing to all devices instead...")
		else:
			log.info("Pushing to channel %s." % channel_tag)
		return req_channel

	def pokemon_alert(self, pkinfo):
		args = {
			'title': replace(self.title, pkinfo),
			'url': replace(self.url, pkinfo),
			'body': replace(self.body, pkinfo)
		}
		try_sending(log, self.connect, "PushBullet", self.sender.push_link, args)
		

		
	
#Setup Logging
import logging
log = logging.getLogger(__name__)

#Python modules

#Local modules
from ..alarm import Alarm
from ..utils import *

#External modules
from pushbullet import PushBullet

class Pushbullet_Alarm(Alarm):

	_defaults = {
		'pokemon':{
			'title':"A wild <pkmn> has appeared!",
			'url':"<gmaps>",
			'body':"Available until <24h_time> (<time_left>)."
		}
	}
	
	#Gather settings and create alarm
	def __init__(self, settings):
		#Service Info
		self.api_key = settings['api_key']
		#Set Alerts
		self.pokemon = self.set_alert(settings.get('pokemon', {}), self._defaults['pokemon'])
		#Connect and send startup message
		self.connect()
		self.startup_message = settings.get('startup_message', "True")
		log.info("Pushbullet Alarm intialized.")
		if parse_boolean(self.startup_message):
			push = self.pokemon['sender'].push_note("PokeAlarm activated!", "We will alert you about pokemon.")
	
	#Attempt to get the channel, otherwise default to all devices
	def get_sender(self, client, channel_tag):
		req_channel = next((channel for channel in client.channels if channel.channel_tag == channel_tag), self.client)
		if req_channel is self.client and channel_tag is not None:
			log.error("Unable to find channel... Pushing to all devices instead...")
		else:
			log.info("Pushing to channel %s." % channel_tag)
		return req_channel
	
	#(Re)establishes Pushbullet connection
	def connect(self):
		self.client = PushBullet(self.api_key)
		self.pokemon['sender'] = self.get_sender(self.client, self.pokemon['channel'])
		
	#Set the appropriate settings for each alert
	def set_alert(self, settings, default):
		alert = {}
		alert['title'] = settings.get('title', default['title'])
		alert['url'] = settings.get('url', default['url'])
		alert['body'] = settings.get('body', default['body'])
		alert['channel'] = settings.get('channel')
		return alert
		
	#Trigger an alert based on Pokemon info
	def pokemon_alert(self, pokemon_info):
		self.send_alert(self.pokemon, pokemon_info)
		
	#Send Alert to the Pushbullet
	def send_alert(self, alert, info):
		args = {
			'title': replace(alert['title'], info),
			'url': replace(alert['url'], info),
			'body': replace(alert['body'], info)
		}
		try_sending(log, self.connect, "PushBullet", alert['sender'].push_link, args)
		

		

		
	

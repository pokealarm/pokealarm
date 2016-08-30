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
		},
		'pokestop':{
			'title':"Someone has placed a lure on a Pokestop!",
			'url':"<gmaps>",
			'body':"Lure will expire at <24h_time> (<time_left>)."
		},
		'gym':{
			'title':"A Team <old_team> gym has fallen!",
			'url':"<gmaps>",
			'body':"It is now controlled by <new_team>."
		}
	}
	
	#Gather settings and create alarm
	def __init__(self, settings):
		#Service Info
		self.api_key = settings['api_key']
		self.startup_message = settings.get('startup_message', "True")
		
		#Set Alerts
		self.pokemon = self.set_alert(settings.get('pokemon', {}), self._defaults['pokemon'])
		self.pokestop = self.set_alert(settings.get('pokestop', {}), self._defaults['pokestop'])
		self.gym = self.set_alert(settings.get('gyms', {}), self._defaults['gym'])
		
		#Connect and send startup message
		self.connect()
		if parse_boolean(self.startup_message):
			push = self.pokemon['sender'].push_note("PokeAlarm activated!", "We will alert you about pokemon.")
		log.info("Pushbullet Alarm intialized.")
	
	#(Re)establishes Pushbullet connection
	def connect(self):
		self.client = PushBullet(self.api_key)
		self.pokemon['sender'] = self.get_sender(self.client, self.pokemon['channel'])
		self.pokestop['sender'] = self.get_sender(self.client, self.pokestop['channel'])
		self.gym['sender'] = self.get_sender(self.client, self.gym['channel'])
		
	#Set the appropriate settings for each alert
	def set_alert(self, settings, default):
		alert = {}
		alert['title'] = settings.get('title', default['title'])
		alert['url'] = settings.get('url', default['url'])
		alert['body'] = settings.get('body', default['body'])
		alert['channel'] = settings.get('channel')
		return alert
	
			
	#Send Alert to Pushbullet
	def send_alert(self, alert, info):
		args = {
			'title': replace(alert['title'], info),
			'url': replace(alert['url'], info),
			'body': replace(alert['body'], info)
		}
		try_sending(log, self.connect, "PushBullet", alert['sender'].push_link, args)
		
	#Trigger an alert based on Pokemon info
	def pokemon_alert(self, pokemon_info):
		self.send_alert(self.pokemon, pokemon_info)
		
	#Trigger an alert based on Pokestop info
	def pokestop_alert(self, pokestop_info):
		self.send_alert(self.pokestop, pokestop_info)
		
	#Trigger an alert based on Gym info
	def gym_alert(self, gym_info):
		self.send_alert(self.gym, gym_info)
		
	#Attempt to get the channel, otherwise default to all devices
	def get_sender(self, client, channel_tag):
		req_channel = next((channel for channel in client.channels if channel.channel_tag == channel_tag), self.client)
		if req_channel is self.client and channel_tag is not None:
			log.error("Unable to find channel... Pushing to all devices instead...")
		else:
			log.info("Pushing to channel %s." % channel_tag)
		return req_channel
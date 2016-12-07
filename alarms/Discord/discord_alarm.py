#Setup Logging
import logging
log = logging.getLogger(__name__)

#Python modules
import re

#Local modules
from ..alarm import Alarm
from ..utils import *

#External modules
import requests

class Discord_Alarm(Alarm):

	_defaults = {
		'pokemon':{
			'username':"<pkmn>",
			'icon_url' : "https://raw.githubusercontent.com/kvangent/PokeAlarm/master/icons/<id>.png",
			'title':"<pkmn> with <iv>% (<atk>/<def>/<sta>) has spawned!",
			'url':"<gmaps>",
			'body': "In <city>, Available until <24h_time> (<time_left>)."
		},
		'pokestop':{
			'username':"Pokestop",
			'icon_url' : "https://raw.githubusercontent.com/kvangent/PokeAlarm/master/icons/pokestop.png",
			'title':"Someone has placed a lure on a Pokestop!",
			'url':"<gmaps>",
			'body':"Lure will expire at <24h_time> (<time_left>)."
		},
		'gym':{
			'username':"<new_team> Gym Alerts",
			'icon_url' : "https://raw.githubusercontent.com/kvangent/PokeAlarm/master/icons/gym_<new_team>.png",
			'title':"A Team <old_team> gym has fallen!",
			'url':"<gmaps>",
			'body': "It is now controlled by <new_team>."
		}
	}

	#Gather settings and create alarm
	def __init__(self, settings):
		#Service Info
		self.api_key = settings['api_key']
		self.startup_message = settings.get('startup_message', "True")
		self.map = settings.get('map', {})
		self.statup_list = settings.get('startup_list', "true")

		#Set Alerts
		self.pokemon = self.set_alert(settings.get('pokemon', {}), self._defaults['pokemon'])
		self.pokestop = self.set_alert(settings.get('pokestop', {}), self._defaults['pokestop'])
		self.gym = self.set_alert(settings.get('gym', {}), self._defaults['gym'])

		#Connect and send startup messages
		#self.connect()
		if parse_boolean(self.startup_message):
			args = {
				'username': 'PokeAlarm',
				'content': 'PokeAlarm activated! We will alert this channel about pokemon.'
			}
			self.send_webhook(**args)
		log.info("discord Alarm initialized.")
	
	#Establish connection with Discord
	def connect(self):
		pass
    
	#Set the appropriate settings for each alert
	def set_alert(self, settings, default):
		alert = {}
		alert['username'] = settings.get('username', default['username'])
		alert['icon_url'] = settings.get('icon_url', default['icon_url'])
		alert['title'] = settings.get('title', default['title'])
		alert['url'] = settings.get('url', default['url'])
		alert['body'] = settings.get('body', default['body'])
		
		return alert
		
	#Send Alert to Discord
	def send_alert(self, alert, info):
		args = {
			'username': replace(alert['username'], info),
			'title': replace(alert['title'], info),
			'url': replace(alert['url'], info),
			'description': replace(alert['body'], info),
			'thumbnail': replace(alert['icon_url'], info)
		}
		try_sending(log, self.connect, "Discord", self.send_webhook, args)
	
	def send_webhook(self, **args):
		if 'content' in args:
			data = {
				'username': args['username'],
				'content': args['content']
			}
		else:
			data = {
				'username': args['username'],
				'embeds': [{
					'title': args['title'],
					'url': args['url'],
					'description': args['description'],
					'thumbnail': {'url': args['thumbnail']}
				}]
			}
		try:
			requests.post(self.api_key, json=data, timeout=(None, 1))
		except requests.exceptions.ReadTimeout:
			log.debug('Response timeout on webhook endpoint %s', self.api_key)
		except requests.exceptions.RequestException as e:
			log.debug(e)

	

	#Trigger an alert based on Pokemon info
	def pokemon_alert(self, pokemon_info):
		self.send_alert(self.pokemon, pokemon_info)
		
	#Trigger an alert based on Pokestop info
	def pokestop_alert(self, pokestop_info):
		self.send_alert(self.pokestop, pokestop_info)
		
	#Trigger an alert based on Pokestop info
	def gym_alert(self, gym_info):
		self.send_alert(self.gym, gym_info)

#Setup Logging
import logging
log = logging.getLogger(__name__)

#Python modules

#Local modules
from ..alarm import Alarm
from ..utils import *

#External modules
import telepot
 
class Telegram_Alarm(Alarm):
 	
	_defaults = {
		'pokemon':{
			'chat_id':None,
			'title': "A wild <pkmn> has appeared!",
			'body': "<gmaps> \n Available until <24h_time> (<time_left>).",
			'location': "True"
		}
	}
	
	#Gather settings and create alarm
	def __init__(self, settings):
		#Service Info
		self.bot_token = settings['bot_token']
		self.startup_message = settings.get('startup_message', "True")
		
		#Set Alerts
		self.pokemon = self.set_alert(settings.get('pokemon', {}), self._defaults['pokemon'])
		
		#Connect and send startup message
 		self.connect()
		if parse_boolean(self.startup_message):
			self.client.sendMessage(self.pokemon['chat_id'], 'PokeAlarm activated! We will alert this chat about pokemon.')
		log.info("Telegram Alarm intialized.")
	
	#(Re)establishes Telegram connection
	def connect(self):
		self.client = telepot.Bot(self.bot_token) 
		
	#Set the appropriate settings for each alert
	def set_alert(self, settings, default):
		alert = {}
		
		alert['chat_id'] = settings['chat_id']
		
		alert['title'] = settings.get('title', default['title'])
		alert['body'] = settings.get('body', default['body'])
		alert['location'] = parse_boolean(settings.get('location', default['location']))
		
		return alert
 		
	#Send Alert to Telegram
 	def send_alert(self, alert, info):
		args = {
			'chat_id': alert['chat_id'],
			'text': '<b>' + replace(alert['title'], info) + '</b> \n' + replace(alert['body'], info),
			'parse_mode': 'HTML',
			'disable_web_page_preview': 'False',
		}
		try_sending(log, self.connect, "Telegram", self.client.sendMessage, args)
		
		if alert['location']:
			locargs = { 
				'chat_id': alert['chat_id'],
				'latitude': info['lat'],
				'longitude':  info['lng'],
				'disable_notification': 'True'
			}
			try_sending(log, self.connect, "Telegram (Loc)", self.client.sendLocation, locargs)
			
	#Trigger an alert based on Pokemon info
	def pokemon_alert(self, pokemon_info):
		self.send_alert(self.pokemon, pokemon_info)

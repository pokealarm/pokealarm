#Setup Logging
import logging
log = logging.getLogger(__name__)

#Python modules
import httplib
import urllib

#Local modules
from ..alarm import Alarm
from ..utils import *

#External modules

class Boxcar_Alarm(Alarm):

	_defaults = {
		'pokemon':{
			'title':"A wild <pkmn> has appeared!",
			'long_message':"Available <a href='<gmaps>'>here</a> until <24h_time> (<time_left>).",
			'icon_url':"https://raw.githubusercontent.com/kvangent/PokeAlarm/master/icons/<id>.png",
			'sound':"beep-crisp"
		},
		'pokestop':{
			'title':"Someone has placed a lure on a Pokestop!",
			'long_message':"<a href='<gmaps>'>This lure</a> will expire at <24h_time> (<time_left>).",
			'icon_url':"https://raw.githubusercontent.com/kvangent/PokeAlarm/master/icons/pokestop.png",
			'sound':"beep-crisp"
		},
		'gym':{
			'title':"A Team <old_team> gym has fallen!",
			'long_message':"<a href='<gmaps>'>Gym</a> is now controlled by <new_team>.",
			'icon_url':"https://raw.githubusercontent.com/kvangent/PokeAlarm/master/icons/gym.png",
			'sound':"beep-crisp"
		}
	}
	
	#Gather settings and create alarm
	def __init__(self, settings):
		#Service Info
		self.user_credentials = settings['user_credentials']
		self.startup_message = settings.get('startup_message', "True")
		self.startup_list = settings.get('startup_list', "True")
		
		#Set Alerts
		self.pokemon = self.set_alert(settings.get('pokemon', {}), self._defaults['pokemon'])
		self.pokestop = self.set_alert(settings.get('pokestop', {}), self._defaults['pokestop'])
		self.gym = self.set_alert(settings.get('gyms', {}), self._defaults['gym'])
		
		#Connect and send startup messages
		if parse_boolean(self.startup_message):
			self.send_boxcar("PokeAlarm activated!", "We will alert you about pokemon.")
		if parse_boolean(self.startup_list):
			for line in notify_list_multi_msgs(config["NOTIFY_LIST"],4000,"We will alert this channel of the following pokemon"):
				self.send_boxcar(line, 'We will alert this channel of the following pokemon',icon_url="https://raw.githubusercontent.com/kvangent/PokeAlarm/master/icons/PokemonGo.png",sound=self.pokemon['sound'])
		log.info("Boxcar Alarm intialized.")
	
		
	#Set the appropriate settings for each alert
	def set_alert(self, settings, default):
		alert = {}
		alert['title'] = settings.get('title', default['title'])
		alert['long_message'] = settings.get('long_message', default['long_message'])
		alert['icon_url'] = settings.get('icon_url', default['icon_url'])
		alert['sound'] = settings.get('sound', default['sound'])
		return alert
			
	#Send Alert to Pushbullet
	def send_alert(self, alert, info):
		args = {
			'title': replace(alert['title'], info),
			'long_message': replace(alert['long_message'], info),
			'icon_url': replace(alert['icon_url'], info),
			'sound': replace(alert['sound'], info),
		}
		try_sending(log, self.connect, "Boxcar", self.send_boxcar, args)
		
	#Trigger an alert based on Pokemon info
	def pokemon_alert(self, pokemon_info):
		self.send_alert(self.pokemon, pokemon_info)
		
	#Trigger an alert based on Pokestop info
	def pokestop_alert(self, pokestop_info):
		self.send_alert(self.pokestop, pokestop_info)
		
	#Trigger an alert based on Gym info
	def gym_alert(self, gym_info):
		self.send_alert(self.gym, gym_info)
		
	def send_boxcar(self, title='PokeAlert', long_message=None, url=None, icon_url=None, sound=None):
		#Establish connection
		connection = httplib.HTTPSConnection("new.boxcar.io:443", timeout=10)
		payload = {"user_credentials": self.user_credentials, 
				"notification[title]": title,
				"notification[long_message]": long_message,
				"notification[icon_url]": icon_url,
				"sound": sound}	
		if url is not None:
			payload["notification[open_url]"] = url
		connection.request("POST", "/api/notifications", urllib.urlencode(payload), 
			{"Content-Type": "application/x-www-form-urlencoded"})
		r = connection.getresponse()
		if r.status != 201:
			raise httplib.HTTPException("Response not 201")
	
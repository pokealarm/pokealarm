#Setup Logging
import logging
log = logging.getLogger(__name__)

#Python modules
import re

#Local modules
from ..alarm import Alarm
from ..utils import *

#External modules
from slacker import Slacker

class Slack_Alarm(Alarm):

	_defaults = {
		'pokemon':{
			#'channel':"general",
			'username':"<pkmn>",
			'icon_url' : "https://raw.githubusercontent.com/kvangent/PokeAlarm/master/icons/<id>.png",
			'title':"A wild <pkmn> has appeared!",
			'url':"<gmaps>",
			'body': "Available until <24h_time> (<time_left>)."
		},
		'pokestop':{
			#'channel':"general",
			'username':"Pokestop",
			'icon_url' : "https://raw.githubusercontent.com/kvangent/PokeAlarm/master/icons/pokestop.png",
			'title':"Someone has placed a lure on a Pokestop!",
			'url':"<gmaps>",
			'body':"Lure will expire at <24h_time> (<time_left>)."
		},
		'gym':{
			#'channel':"general",
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
		self.channel = settings.get('channel', "general")
		self.map = settings.get('map', {})
		self.startup_list = settings.get('startup_list', "True")
                self.at_channel_on_perfect = settings.get('at_channel_on_perfect', "False")
		
		#Set Alerts
		self.pokemon = self.set_alert(settings.get('pokemon', {}), self._defaults['pokemon'])
		self.pokestop = self.set_alert(settings.get('pokestop', {}), self._defaults['pokestop'])
		self.gym = self.set_alert(settings.get('gym', {}), self._defaults['gym'])
		
		#Connect and send startup messages
		self.connect()
		if parse_boolean(self.startup_message):
			self.client.chat.post_message(
				channel=self.get_channel(self.pokemon['channel']),
				username='PokeAlarm',
				text='PokeAlarm activated! We will alert this channel about pokemon.'
			)
		log.info("Slack Alarm intialized.")
		log.debug("Attempting to push to the following channels: Pokemon:%s, Pokestops:%s, Gyms:%s" %(self.pokemon['channel'], self.pokestop['channel'], self.gym['channel']))

	#Establish connection with Slack
	def connect(self):
		self.client = Slacker(self.api_key)
		self.update_channels()
	
	#Set the appropriate settings for each alert
	def set_alert(self, settings, default):
		alert = {}
		alert['channel'] = settings.get('channel', self.channel)
		alert['username'] = settings.get('username', default['username'])
		alert['icon_url'] = settings.get('icon_url', default['icon_url'])
		alert['title'] = settings.get('title', default['title'])
		alert['url'] = settings.get('url', default['url'])
		alert['body'] = settings.get('body', default['body'])
                alert['body_with_at_channel'] = "{} - <!channel>".format(alert['body'])
		
		alert['map'] = get_static_map_url(settings.get('map', self.map))
		
		return alert

	#Send Alert to Slack
	def send_alert(self, alert, info):		
		args = {
			'channel': self.get_channel(replace(alert['channel'], info)),
			'username': replace(alert['username'], info),
                        'text': '<{}|{}> - {}'.format(replace(alert['url'], info),  replace(alert['title'], info) , replace(alert['body_with_at_channel'] if info['iv'] == '100.00' and parse_boolean(self.at_channel_on_perfect) and '<!channel>' not in alert['body'] else alert['body'], info)),
			'icon_url': replace(alert['icon_url'], info),
			'attachments': self.make_map(alert['map'], info['lat'], info['lng'])
		}
			
		try_sending(log, self.connect, "Slack", self.client.chat.post_message, args)
		
	#Trigger an alert based on Pokemon info
	def pokemon_alert(self, pokemon_info):
		self.send_alert(self.pokemon, pokemon_info)
		
	#Trigger an alert based on Pokestop info
	def pokestop_alert(self, pokestop_info):
		self.send_alert(self.pokestop, pokestop_info)
		
	#Trigger an alert based on Pokestop info
	def gym_alert(self, gym_info):
		self.send_alert(self.gym, gym_info)
	
	#Update channels list
	def update_channels(self):
		self.channels = dict()
		response = self.client.channels.list(True).body
		for channel in response['channels']:
			self.channels[channel['name']] = channel['id']
		response = self.client.groups.list().body
		for channel in response['groups']:
			self.channels[channel['name']] = channel['id']
		log.debug(self.channels)
	
	#Checks for valid channel, otherwise defaults to general
	def get_channel(self, name):
		channel = self.channel_format(name)
		if channel not in self.channels:
			if name == self.channel:
				log.error("Default channel %s not found... Posting to general instead." % channel)
				return "#general"
			else:
				log.debug("No channel created named %s... Reverting to default." % channel)
				default = self.get_channel(self.channel)
				return default
		return channel
	
	#Returns a string s that is in proper channel format
	def channel_format(self, name):
		if name[0] == '#': #Remove # if added 
			name = name[1:]
		name = name.replace(u"\u2642", "m").replace(u"\u2640", "f").lower()
		pattern = re.compile("[^_a-z0-9-]+")
		return pattern.sub("", name)

	# Build a query for a static map of the pokemon location
	def make_map(self, map_url, lat, lng):
		if map_url is None: #If no map is set
			return None
		map = [
			{
				'fallback': 'Map_Preview',
				'image_url':  replace(map_url, {'lat':lat, 'lng':lng} )
			}
		]
		log.debug(map[0].get('image_url'))
		return map

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

	#Gather settings and create alarm
	def __init__(self, settings):
		self.api_key = settings['api_key']
		self.connect()
		self.channel = settings.get('channel', "general")
		self.title = settings.get('title', "A wild <pkmn> has appeared!")
		self.url = settings.get('url', "<gmaps>")
		self.body = settings.get('body', "Available until <24h_time> (<time_left>).")
		self.username = settings.get('username', "<pkmn>")
		self.setup_map(settings.get('map', {}))
		log.info("Slack Alarm intialized.")
		self.post_message(
			channel=self.channel,
			username='PokeAlarm',
			text='PokeAlarm activated! We will alert this channel about pokemon.'
		)
	
	#Establish connection with Slack
	def connect(self):
		self.client = Slacker(self.api_key)
		self.update_channels()
	
	#Update channels list
	def update_channels(self):
		self.channels = set()
		response = self.client.channels.list().body
		for channel in response['channels']:
			self.channels.add(channel['name'])
		response = self.client.groups.list().body
		for channel in response['groups']:
			self.channels.add(channel['name'])
		log.debug(self.channels)
	
	#Returns a string s that is in proper channel format
	def channel_format(self, name):
		if name[0] == '#': #Remove # if added 
			name = name[1:]
		name = name.replace(u"\u2642", "m").replace(u"\u2640", "f").lower()
		pattern = re.compile("[^a-z0-9-]+")
		return pattern.sub("", name)
	
	#Checks for valid channel, otherwise defaults to general
	def get_channel(self, name):
		channel = self.channel_format(name)
		if channel not in self.channels:
			log.debug("No channel created named %s... Posting to general instead." % channel)
			return "#general"
		return channel

	#Post a message to channel
	def post_message(self, channel, username, text, icon_url=None, map=None):
		args = {
			'channel': self.get_channel(channel),
			'username': username,
			'text': text,
			'icon_url': icon_url,
		}
		
		if map is not None:
			args['attachments'] = map
			
		try_sending(log, self.connect, "Slack", self.client.chat.post_message, args)
	
	#Send Pokemon Info to Slack
	def pokemon_alert(self, pkinfo):
		channel = replace(self.channel, pkinfo)
		username = replace(self.username, pkinfo)
		text = '<{}|{}> {}'.format(replace(self.url, pkinfo),  replace(self.title, pkinfo) , replace(self.body, pkinfo))
		icon_url = 'https://raw.githubusercontent.com/kvangent/PokeAlarm/master/icons/{}.png'.format(pkinfo['id'])
		map = self.get_map_url(pkinfo['lat'], pkinfo['lng'])
		self.post_message(channel, username, text, icon_url, map)
			
	#Set stack map attributes
	def setup_map(self, settings):
		if parse_boolean(settings.get('enabled', "True")) is False:
			self.map = None
			return
		width = settings.get('width', '250')
		height = settings.get('height', '125')
		maptype = settings.get('maptype', 'roadmap')
		zoom = settings.get('zoom', '15')
	
		center = '<CENTER>'
		query_center = 'center={}'.format(center)
		query_markers =  'markers=color:red%7C{}'.format(center)
		query_size = 'size={}x{}'.format(width, height)
		query_zoom = 'zoom={}'.format(zoom)
		query_maptype = 'maptype={}'.format(maptype)
		
		self.map = ('https://maps.googleapis.com/maps/api/staticmap?' +
					query_center + '&' + query_markers + '&' +
					query_maptype + '&' + query_size + '&' + query_zoom)
	
	# Build a query for a static map of the pokemon location
	def get_map_url(self, lat, lng):
		if self.map is None: #If no map is set
			return None
		map = [
			{
				'fallback': 'Map_Preview',
				'image_url':  self.map.replace('<CENTER>', '{},{}'.format(lat,lng))
			}
		]
		return map
		

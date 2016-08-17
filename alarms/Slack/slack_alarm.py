#!/usr/bin/python
# -*- coding: utf-8 -*-

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
		self.username = settings.get('username', u'<pedestrian>[<g_distance><bearing_arrow>\u231A<g_duration>m]<pkmn>')
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
	def post_message(self, channel, username, text, icon_url=None):
		args = {
			'channel': self.get_channel(channel),
			'username': username,
			'text': text,
			'icon_url': icon_url
		}
		try_sending(log, self.connect, "Slack", self.client.chat.post_message, args)
		
	
	#Send Pokemon Info to Slack
	def pokemon_alert(self, pkinfo):
		channel = replace(self.channel, pkinfo).encode("utf-8")
		username = replace(self.username, pkinfo).encode("utf-8"),
		text = '<{}|{}> {}'.format(replace(self.url, pkinfo).encode("utf-8"),  replace(self.title, pkinfo).encode("utf-8") , replace(self.body, pkinfo).encode("utf-8")),
		icon_url = 'https://raw.githubusercontent.com/PokemonGoMap/PokemonGo-Map/develop/static/icons/{}.png'.format(pkinfo['id'])
		self.post_message(channel, username, text, icon_url)
		

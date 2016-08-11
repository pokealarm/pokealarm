#Setup Logging
import logging
log = logging.getLogger(__name__)

#Local modules
from alarm import Alarm
from slacker import Slacker
from utils import *


class Slack_Alarm(Alarm):

	def __init__(self, settings):
		self.api_key = settings['api_key']
		self.connect()
		self.channel = settings['channel']
		self.pkmn_channel =  settings.get('pkmn_channel')
		self.title = settings.get('title', "A wild <pkmn> has appeared!")
		self.url = settings.get('url', "<gmaps>")
		self.body = settings.get('body', "Available until <24h_time> (<time_left>).")
		self.username = settings.get('username', "<pkmn>")
		log.info("Slack Alarm intialized")
		self.client.chat.post_message(
			channel=self.channel,
			username='PokeAlarm',
			text='PokeAlarm activated! We will alert this channel about pokemon.'
		)
		
	def connect(self):
		self.client = Slacker(self.api_key)
		
	def pokemon_alert(self, pkinfo):
		channel = self.channel if self.pkmn_channel is None else replace(self.pkmn_channel, pkinfo)
		title = replace(self.title, pkinfo)
		link = replace(self.url, pkinfo)
		body =  replace(self.body, pkinfo)
		args = {
			'channel': channel.replace(u"\u2642", "M").replace(u"\u2640", "F"),
			'username': replace(self.username, pkinfo),
			'text': '<{}|{}> {}'.format(link,  title , body),
			'icon_url': 'https://raw.githubusercontent.com/PokemonGoMap/PokemonGo-Map/develop/static/icons/{}.png'.format(pkinfo['id'])
		}
		try_sending(log, self.connect, "Slack", self.client.chat.post_message, args)

#Setup Logging
import logging
log = logging.getLogger(__name__)

#Local modules
from alarm import Alarm
from slacker import Slacker
from utils import *


class Slack_Alarm(Alarm):

	def __init__(self, settings):
		self.client = Slacker(settings['api_key'])
		self.channel = settings['channel']
		self.pkmn_channel =  settings.get('pkmn_channel')
		self.notify_text = settings.get('notify_text', "A wild <pkmn> has appeared!")
		self.notify_link = settings.get('notify_link', "<gmaps>")
		self.body_text = settings.get('body_text', "Available until <24h_time> (<time_left>).")
		self.username = settings.get('username', "<pkmn>")
		log.info("Slack Alarm intialized")
		self.client.chat.post_message(
			channel=self.channel,
			username='PokeAlarm',
			text='PokeAlarm activated! We will alert this channel about pokemon.'
		)
		
	def pokemon_alert(self, pkinfo):
		channel = self.channel if self.pkmn_channel is None else replace(self.pkmn_channel, pkinfo)
		username = replace(self.username, pkinfo)
		notify_text = replace(self.notify_text, pkinfo)
		link = replace(self.notify_link, pkinfo)
		body_text =  replace(self.body_text, pkinfo)
		self.client.chat.post_message(
			channel=channel.replace(u"\u2642", "M").replace(u"\u2640", "F"),
			username=username,
			text='<{}|{}> {}'.format(link,  notify_text , body_text),
			icon_url='https://raw.githubusercontent.com/PokemonGoMap/PokemonGo-Map/master/static/icons/{id}.png'.format(**pkinfo)
		)
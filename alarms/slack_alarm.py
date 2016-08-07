import logging
from alarm import Alarm
from slacker import Slacker
from utils import *


log = logging.getLogger(__name__)


class Slack_Alarm(Alarm):

	def __init__(self, settings):
		self.client = Slacker(settings['api_key'])
		self.channel = settings['channel']
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
		notify_text = replace(self.notify_text, pkinfo).encode("utf-8")
		link = replace(self.notify_link, pkinfo).encode("utf-8")
		body_text =  replace(self.body_text, pkinfo).encode("utf-8")
		username = replace(self.username, pkinfo).encode("utf-8")
		self.client.chat.post_message(
			channel=self.channel,
			username=username,
			text='<{}|{}> {}'.format(link,  notify_text , body_text),
			icon_url='https://raw.githubusercontent.com/PokemonGoMap/PokemonGo-Map/master/static/icons/{id}.png'.format(**pkinfo)
		)
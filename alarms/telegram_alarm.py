import logging
import telepot
 
from alarm import Alarm
from utils import *
 
log = logging.getLogger(__name__)
 
class Telegram_Alarm(Alarm):
 	
	def __init__(self, settings):
		self.bot_token = settings['bot_token']
 		self.connect()
 		self.chat_id = settings['chat_id']
		self.title = settings.get('title', "A wild <pkmn> has appeared!")
		self.body = settings.get('body', "<gmaps> \n Available until <24h_time> (<time_left>).")
		log.info("Telegram Alarm intialized")
		self.client.sendMessage(self.chat_id, 'PokeAlarm activated! We will alert this chat about pokemon.')
		
	def connect(self):
		self.client = telepot.Bot(self.bot_token) 
 		
 	def pokemon_alert(self, pkinfo):
		title = replace(self.title, pkinfo)
		body =  replace(self.body, pkinfo)
		args = {
			'chat_id': self.chat_id,
			'text': '<b>' + title + '</b> \n' + body,
			'parse_mode': 'HTML',
			'disable_web_page_preview': 'False'
		}
		try_sending(log, self.connect, "Telegram", self.client.sendMessage, args)
				
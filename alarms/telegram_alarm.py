import logging
import telepot
 
from alarm import Alarm
from utils import *
 
log = logging.getLogger(__name__)
 
class Telegram_Alarm(Alarm):
 	
	def __init__(self, settings):
 		self.client = telepot.Bot(settings['bot_token']) 
 		self.channel = settings['chat_id']
		self.header = settings.get('header', "A wild <pkmn> has appeared!")
		self.body_text = settings.get('body_text', "<gmaps> \n Available until <24h_time> (<time_left>).")
		log.info("Telegram Alarm intialized")
		self.client.sendMessage(self.channel, 'PokeAlarm activated! We will alert this channel about pokemon.')
 		
 	def pokemon_alert(self, pkinfo):
		header = replace(self.header, pkinfo)
		body_text =  replace(self.body_text, pkinfo)
		message = self.client.sendMessage(self.channel, '<b>' + header + '</b> \n' + body_text, parse_mode='HTML', disable_web_page_preview='False')
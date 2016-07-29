import logging
import telepot
 
from alarm import Alarm
 
log = logging.getLogger(__name__)
 
class Telegram_Alarm(Alarm):
 	
	def __init__(self, settings):
 		self.client = telepot.Bot(settings['bot_token']) 
 		self.channel = settings['chat_id']
		log_msg = "Telegram Alarm intialized"
		if 'name' in settings:
			self.name = settings['name']
			log_mst = log_msg + ": " + self.name
		log.info(log_msg)
		self.client.sendMessage(self.channel, 'PokeAlarm activated! We will alert this channel about pokemon.')
 		
 	def pokemon_alert(self, pkinfo):
		notification_text = pkinfo['alert']
		if hasattr(self, 'name') :
			notification_text = self.name + ": " + notification_text
		gmaps_link = pkinfo['gmaps_link']
		time_text =  pkinfo['time_text']
		message = self.client.sendMessage(self.channel, '<b>' + notification_text + '</b> \n' + gmaps_link + '\n' + time_text, parse_mode='HTML', disable_web_page_preview='False')
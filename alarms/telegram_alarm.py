import logging
import telepot
 
from alarm import Alarm
 
log = logging.getLogger(__name__)
 
class Telegram_Alarm(Alarm):
 	
	def __init__(self, pkinfo):
 		self.client = telepot.Bot(pkinfo['api_key']) 
 		self.channel = chatid
 		log.info("Telegram_Alarm intialized.")
		self.client.sendMessage(self.channel, 'PokeAlarm activated! We will alert this channel about pokemon.')
 		
 	def pokemon_alert(self, pkinfo):
 		notification_text = pkinfo['alert']
		if self.name :
			notification_text = self.name + ": " + notification_text
		gmaps_link = pkinfo['gmaps_link']
		time_text =  pkinfo['time_text']
        self.client.sendMessage(self.channel, '<b>' + notification_text + '</b> \n' + google_maps_link + '\n' + time_text, parse_mode='HTML', disable_web_page_preview='False')

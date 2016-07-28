import logging

from alarm import Alarm
from twilio.rest import TwilioRestClient

log = logging.getLogger(__name__)

class Twilio_Alarm(Alarm):
	
	def __init__(self, settings):
		self.client = TwilioRestClient(settings['account_sid'], settings['auth_token']) 
		self.from_num = settings['from_number']
		self.to_num = settings['to_number']
		log_msg = "Twilio Alarm intialized"
		if 'name' in settings:
			self.name = settings['name']
			log_mst = log_msg + ": " + self.name
		log.info(log_msg)
		self.send_sms("PokeAlarm has been activated! We will text this number about pokemon.")
		
	def pokemon_alert(self, pkinfo):
		notification_text = pkinfo['alert']
		if hasattr(self, 'name') :
			notification_text = self.name + ": " + notification_text
		gmaps_link = pkinfo['gmaps_link']
		time_text =  pkinfo['time_text']
		self.send_sms(notification_text + " " + time_text + " " + gmaps_link)
		
	def send_sms(self, msg):
		message = self.client.messages.create(body=msg,
			to=self.to_num,    
			from_=self.from_num)
import logging

from alarm import Alarm
from twilio.rest import TwilioRestClient
from utils import *

log = logging.getLogger(__name__)

class Twilio_Alarm(Alarm):
	
	def __init__(self, settings):
		self.client = TwilioRestClient(settings['account_sid'], settings['auth_token']) 
		self.from_num = settings['from_number']
		self.to_num = settings['to_number']
		self.message = settings.get('message', 
			"A wild <pkmn> has appeared! <gmaps> Available until <24h_time> (<time_left>).")
		log.info("Twilio Alarm intialized")
		self.send_sms("PokeAlarm has been activated! We will text this number about pokemon.")
		
	def pokemon_alert(self, pkinfo):
		message = replace(self.message, pkinfo)
		self.send_sms(message)
		
	def send_sms(self, msg):
		message = self.client.messages.create(body=msg,
			to=self.to_num,    
			from_=self.from_num)
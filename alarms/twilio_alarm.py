import logging

from alarm import Alarm
from twilio.rest import TwilioRestClient
from utils import *

log = logging.getLogger(__name__)

class Twilio_Alarm(Alarm):
	
	def __init__(self, settings):
		self.account_sid = settings['account_sid']
		self.auth_token = settings['auth_token']
		self.connect()
		self.from_num = settings['from_number']
		self.to_num = settings['to_number']
		self.message = settings.get('message', 
			"A wild <pkmn> has appeared! <gmaps> Available until <24h_time> (<time_left>).")
		log.info("Twilio Alarm intialized")
		self.send_sms("PokeAlarm has been activated! We will text this number about pokemon.")
		
	def connect(self):
		self.client = TwilioRestClient(self.account_sid, self.auth_token) 
		
	def pokemon_alert(self, pkinfo):
		args = { 
			'msg':replace(self.message, pkinfo)
		}
		try_sending(log, self.connect, "Twilio", self.send_sms, args)
		
	def send_sms(self, msg):
		message = self.client.messages.create(body=msg,
			to=self.to_num,    
			from_=self.from_num)
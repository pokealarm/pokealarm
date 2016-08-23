#Setup Logging
import logging
log = logging.getLogger(__name__)

#Python modules

#Local modules
from ..alarm import Alarm
from ..utils import *

#External modules
from twilio.rest import TwilioRestClient

class Twilio_Alarm(Alarm):
	
	#Gather settings and create alarm
	def __init__(self, settings):
		self.account_sid = settings['account_sid']
		self.auth_token = settings['auth_token']
		self.connect()
		self.from_num = settings['from_number']
		self.to_num = settings['to_number']
		self.message = settings.get('message', 
			"A wild <pkmn> has appeared! <gmaps> Available until <24h_time> (<time_left>).")
		self.startup_message = settings.get('startup_message', "True")
		log.info("Twilio Alarm intialized.")
		if parse_boolean(self.startup_message):
		    self.send_sms("PokeAlarm has been activated! We will text this number about pokemon.")
	
	#(Re)establishes Telegram connection
	def connect(self):
		self.client = TwilioRestClient(self.account_sid, self.auth_token) 
	
	#Send Pokemon Info
	def pokemon_alert(self, pkinfo):
		args = { 
			'msg':replace(self.message, pkinfo)
		}
		try_sending(log, self.connect, "Twilio", self.send_sms, args)
		
	#Send message through Twilio
	def send_sms(self, msg):
		message = self.client.messages.create(body=msg,
			to=self.to_num,    
			from_=self.from_num)

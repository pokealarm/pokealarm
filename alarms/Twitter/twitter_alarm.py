#Setup logging
import logging
log = logging.getLogger(__name__)

#Python Modules
from datetime import datetime

#Local Modules
from ..alarm import Alarm
from ..utils import *

#Exernal Modules
from twitter import Twitter, OAuth

class Twitter_Alarm(Alarm):

	#Gather settings and create alarm
	def __init__(self, settings):
		self.token = settings['access_token']
		self.token_key = settings['access_secret']
		self.con_secret = settings['consumer_key']
		self.con_secret_key = settings['consumer_secret']
		self.status = settings.get('status', "A wild <pkmn> has appeared! Available until <24h_time> (<time_left>). <gmaps>")
		self.startup_message = settings.get('startup_message', "True")
		self.connect()
		log.info("Twitter Alarm intialized.")
		if parse_boolean(self.startup_message):
			self.client.statuses.update(status="%s: PokeAlarm has intialized!" % datetime.now().strftime("%H:%M:%S"))
	
	#Establish connection with Twitter
	def connect(self):
		self.client = Twitter(
			auth=OAuth(self.token, self.token_key, self.con_secret, self.con_secret_key))
	
	#Post Pokemon Status
	def pokemon_alert(self, pkinfo):
		args = { "status": replace(self.status, pkinfo)}
		try_sending(log, self.connect, "Twitter", self.client.statuses.update, args)
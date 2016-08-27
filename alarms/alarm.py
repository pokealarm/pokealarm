#Setup Logging
import logging
log = logging.getLogger(__name__)

#Python modules

#Local modules

#External modules

class Alarm(object):
	
	#Gather settings and create alarm
	def __init__(self):
		raise NotImplementedError("This is an abstract method.")
	
	#(Re)establishes Service connection
	def connect():
		raise NotImplementedError("This is an abstract method.")
	
	#Set the appropriate settings for each alert
	def set_alert(self, settings):
		raise NotImplementedError("This is an abstract method.")
	
	#Send Alert to the Service
	def send_alert(self, alert_settings, info):
		raise NotImplementedError("This is an abstract method.")
	
	#Trigger an alert based on Pokemon info
	def pokemon_alert(self, pokemon_info):
		raise NotImplementedError("This is an abstract method.")
	
	#Trigger an alert based on PokeLure info
	def lure_alert(self, pokelure_info):
		raise NotImplementedError("This is an abstract method.")
	
	#Trigger an alert based on PokeGym info
	def gym_alert(self, pokegym_info):
		raise NotImplementedError("This is an abstract method.")	
		
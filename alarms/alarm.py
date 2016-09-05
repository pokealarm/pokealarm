#Setup Logging
from utils import *
log = logging.getLogger(__name__)

#Python modules

#Local modules
from utils import *

#External modules

class Alarm(object):
	
	_defaults = {
		"pokemon":{},
		"lures":{},
		"gyms":{}		
	}
	
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
	def pokestop_alert(self, pokelure_info):
		raise NotImplementedError("This is an abstract method.")
	
	#Trigger an alert based on PokeGym info
	def gym_alert(self, pokegym_info):
		raise NotImplementedError("This is an abstract method.")	
		
	#Apply local filters
	def local_filters(self, element_info):
		#Check if the Pokemon is outside of notify range
		
		log.debug(self.location)
		
		if self.location and self.distance and element_info['latitude'] and element_info['longitude']:
			is_in_range = filter_in_range(self.distance, self.location, [element_info['latitude'], element_info['longitude']])
			if is_in_range:
				log.debug("Element is IN local filter range")
			else:
				log.info("Element NOT IN local filter range")
				
			return is_in_range
		else:
			return True
			
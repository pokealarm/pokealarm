import logging
import json

from datetime import datetime, timedelta

log = logging.getLogger(__name__)

class Alarm(object):
	
	def __init__(self):
		raise NotImplementedError("This is an abstract method")
		
	def pokemon_alert(self, pokemon):
		raise NotImplementedError("This is an abstract method")
		
		
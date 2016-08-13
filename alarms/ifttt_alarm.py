import logging

import httplib, urllib
from alarm import Alarm
from utils import *

log = logging.getLogger(__name__)

class IFTTT_Alarm(Alarm):
    
    def __init__(self, settings):
        self.api_key = settings['api_key']
        self.event = settings['event']
        self.connect()
        self.value1 = settings.get('value1', "<pkmn>")
        self.value2 = settings.get('value2', "<addr>")
        self.value3 = settings.get('value3', "<time_left>")
        log.info("IFTTT Alarm intialized")
    
    def connect(self):
        pass

    def pokemon_alert(self, pkinfo):
        args = {
            'value1': replace(self.value1, pkinfo),
            'value2': replace(self.value2, pkinfo),
            'value3': replace(self.value3, pkinfo)
        }
        try_sending(log, self.connect, "IFTTT", self.send_ifttt, args)
    
    def send_ifttt(self, value1 = None, value2 = None, value3 = None):		
		##Establish connection
		connection = httplib.HTTPSConnection("maker.ifttt.com:443", timeout=10)
		
		payload = {"value1": value1, 
				"value2": value2, 
				"value3": value3}
		
		connection.request("POST", "/trigger/{e}/with/key/{k}/".format(e=self.event,k=self.api_key), urllib.urlencode(payload), 
			{"Content-Type": "application/x-www-form-urlencoded"})
		r = connection.getresponse()
		if r.status != 200:
			raise httplib.HTTPException("Response not 200")
		
        
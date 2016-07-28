import os
import json
import logging
import time
from threading import Lock
from datetime import datetime

from utilities import pkmn_name, pkmn_alert_text, gmaps_link, pkmn_time_text
from . import config
from pushbullet_alarm import Pushbullet_Alarm
from slack_alarm import Slack_Alarm
from twilio_alarm import Twilio_Alarm

log = logging.getLogger(__name__)

class Alarm_Manager:

	def __init__(self):
		filepath = config['ROOT_PATH']
		with open(os.path.join(filepath, 'alarms.json')) as file:
			settings = json.load(file)
			alarm_settings = settings["alarms"]
			self.notify_list = settings["pokemon"]
			self.seen = {}
			self.alarms = []
			self.lock = Lock()
			for alarm in alarm_settings:
				if alarm['active'] == "True" :
					if alarm['type'] == 'pushbullet' :
						self.alarms.append(Pushbullet_Alarm(alarm))
					elif alarm['type'] == 'slack' :
						self.alarms.append(Slack_Alarm(alarm))
					elif alarm['type'] == 'twilio' :
						self.alarms.append(Twilio_Alarm(alarm))
					else:
						log.info("Alarm type not found: " + alarm['type'])
				else:
					log.info("Alarm not activated: " + alarm['type'] + "because value not set to \"True\"")
			
	#Send a notification to alarms about a found pokemon
	def trigger_pkmn(self, pkmn):
		with self.lock:
			if pkmn['encounter_id'] not in self.seen:
				name = pkmn_name(pkmn['pokemon_id'])
				dissapear_time = datetime.utcfromtimestamp(pkmn['disappear_time']);
				pkinfo = {
					'alert': pkmn_alert_text(name),
					'gmaps_link': gmaps_link(pkmn['latitude'], pkmn['longitude']),
					'time_text': pkmn_time_text(dissapear_time),
					'disappear_time': dissapear_time
				}
				self.seen[id] = pkinfo
				if self.notify_list[name] != "True" :
					log.debug(name + " notification was not triggered because alarm is disabled.")
				elif dissapear_time < datetime.utcnow() :
					log.debug(name + " notification was not triggered because alarm is disabled.")
				else:
					log.info(name + " notication was triggered!")
					for alarm in self.alarms:
						alarm.pokemon_alert(pkinfo)
			if len(self.seen) > 10000 :
				self.clear_stale();

	#Send a notication about pokemon lure found
	def notify_lures(self, lures):
		raise NotImplementedError("This method is not yet implimented.")
	
	#Send a notifcation about pokemon gym detected
	def notify_gyms(self, gyms):
		raise NotImplementedError("This method is not yet implimented.")
		
	#clear expired pokemon so that the seen set is not too large
	def clear_stale(self):
		old = []
		for id in self.seen:
			if self.seen[id]['disappear_time'] < datetime.utcnow() :
				old.append(id)
		for id in old:
			del self.seen[id]
	
	
import os
import json
import logging
import time
from datetime import datetime
from threading import Thread

from utilities import pkmn_name, pkmn_alert_text, gmaps_link, pkmn_time_text
from . import config
from pushbullet_alarm import Pushbullet_Alarm
from slack_alarm import Slack_Alarm
from twilio_alarm import Twilio_Alarm
from telegram_alarm import Telegram_Alarm

log = logging.getLogger(__name__)

class Alarm_Manager(Thread):

	def __init__(self, queue):
		super(Alarm_Manager, self).__init__()
		filepath = config['ROOT_PATH']
		with open(os.path.join(filepath, 'alarms.json')) as file:
			settings = json.load(file)
			alarm_settings = settings["alarms"]
			self.notify_list = settings["pokemon"]
			self.seen = {}
			self.alarms = []
			self.queue = queue
			for alarm in alarm_settings:
				if alarm['active'] == "True" :
					if alarm['type'] == 'pushbullet' :
						self.alarms.append(Pushbullet_Alarm(alarm))
					elif alarm['type'] == 'slack' :
						self.alarms.append(Slack_Alarm(alarm))
					elif alarm['type'] == 'twilio' :
						self.alarms.append(Twilio_Alarm(alarm))
					elif alarm['type'] == 'telegram' :
						self.alarms.append(Telegram_Alarm(alarm))
					else:
						log.info("Alarm type not found: " + alarm['type'])
				else:
					log.info("Alarm not activated: " + alarm['type'] + " because value not set to \"True\"")
	
	#threaded loop to process request data from the queue 
	def run(self):
		log.info("Alarm_Manager has started!")
		while True:
			for i in range(1000):
				data = self.queue.get(block=True)
				self.queue.task_done()
				if data['type'] == 'pokemon' :
					if data['message']['encounter_id'] not in self.seen:
						log.debug("Pokemon data object processing.")
						self.trigger_pkmn(data['message'])
				elif data['type'] == 'pokestop' : 
					log.debug("Pokestop notifications not yet implimented.")
					#do nothing
				elif data['type'] == 'pokegym' :
					log.debug("Pokegym notifications not yet implimented.")
			self.clear_stale();
			
	#Send a notification to alarms about a found pokemon
	def trigger_pkmn(self, pkmn):
		if pkmn['encounter_id'] not in self.seen:
			name = pkmn_name(pkmn['pokemon_id'])
			dissapear_time = datetime.utcfromtimestamp(pkmn['disappear_time']);
			pkinfo = {
				'alert': pkmn_alert_text(name),
				'gmaps_link': gmaps_link(pkmn['latitude'], pkmn['longitude']),
				'time_text': pkmn_time_text(dissapear_time),
				'disappear_time': dissapear_time
			}
			self.seen[pkmn['encounter_id']] = pkinfo
			if self.notify_list[name] != "True" :
				log.info(name + " notification was not triggered because alarm is disabled.")
			elif dissapear_time < datetime.utcnow() :
				log.info(name + " notification was not triggered because time_left had passed.")
			else:
				log.info(name + " notication was triggered!")
				for alarm in self.alarms:
					alarm.pokemon_alert(pkinfo)

			

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
	
	
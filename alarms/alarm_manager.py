import os
import json
import logging
import time
from datetime import datetime

from utilities import pkmn_name, pkmn_alert_text, gmaps_link, pkmn_time_text
from . import config
from pushbullet_alarm import Pushbullet_Alarm
from slack_alarm import Slack_Alarm
from twilio_alarm import Twilio_Alarm
from telegram_alarm import Telegram_Alarm

log = logging.getLogger(__name__)

class Alarm_Manager:

	def __init__(self):
		filepath = config['ROOT_PATH']
		with open(os.path.join(filepath, 'alarms.json')) as file:
			settings = json.load(file)
			alarm_settings = settings["alarms"]
			self.notify_list = settings["pokemon"]
			self.seen = {}        # key: encounter_id, value: pkinfo
			self.lured_seen = {}  # key: pokestop_id, value: pkinfo
			self.alarms = []
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

	#Send a notification to alarms about a found pokemon
	def trigger_pkmn(self, pkmn):
		if 'encounter_id' in pkmn:
			trigger_normal_pkmn(self, pkmn)
		elif 'pokestop_id' in pkmn:
			trigger_lured_pkmn(self, pkmn)
		else:
			raise ValueError("Pokemon is not normal nor lured.")


	#Send a notication about pokemon lure found
	def notify_lures(self, lures):
		raise NotImplementedError("This method is not yet implimented.")

	#Send a notifcation about pokemon gym detected
	def notify_gyms(self, gyms):
		raise NotImplementedError("This method is not yet implimented.")

	#clear expired pokemon so that the seen set is not too large
	def clear_stale(self, normal=False, lured=False):
		if normal:
			old = []
			for id in self.seen:
				if self.seen[id]['disappear_time'] < datetime.utcnow():
					old.append(id)
			for id in old:
				del self.seen[id]
		elif lured:
			old = []
			for id in self.lured_seen:
				if self.lured_seen[id]['disappear_time'] < datetime.utcnow():
					old.append(id)
			for id in old:
				del self.lured_seen[id]

def trigger_normal_pkmn(self, pkmn):
	if pkmn['encounter_id'] not in self.seen:
		name = pkmn_name(pkmn['pokemon_id'])
		disappear_time = datetime.utcfromtimestamp(pkmn['disappear_time']);
		pkinfo = {
			'id': pkmn['pokemon_id'],
			'name': name,
			'alert': pkmn_alert_text(name),
			'gmaps_link': gmaps_link(pkmn['latitude'], pkmn['longitude']),
			'time_text': pkmn_time_text(disappear_time),
			'disappear_time': disappear_time
			}
		self.seen[pkmn['encounter_id']] = pkinfo
		if self.notify_list[name] != "True" :
			log.info(name + " notification was not triggered because alarm is disabled.")
		elif disappear_time < datetime.utcnow() :
			log.info(name + " notification was not triggered because time_left had passed.")
		else:
			log.info(name + " notication was triggered!")
			for alarm in self.alarms:
				alarm.pokemon_alert(pkinfo)
		if len(self.seen) > 10000 :
			self.clear_stale(normal=True);

def trigger_lured_pkmn(self, pkmn):
	disappear_time = datetime.utcfromtimestamp(pkmn['disappear_time']);
	# Only process if this is a new lured pokestop or if the pokestop's pokemon
	# has a new disappear time that is greater than the last one.
	if (pkmn['pokestop_id'] not in self.lured_seen
			or self.lured_seen[pkmn['pokestop_id']]['disappear_time'] < disappear_time):
		name = pkmn_name(pkmn['pokemon_id'])
		pkinfo = {
			'id': pkmn['pokemon_id'],
			'name': name,
			'alert': pkmn_alert_text(name),
			'gmaps_link': gmaps_link(pkmn['latitude'], pkmn['longitude']),
			'time_text': pkmn_time_text(disappear_time),
			'disappear_time': disappear_time
			}
		self.lured_seen[pkmn['pokestop_id']] = pkinfo
		if self.notify_list[name] != "True" :
			log.info(name + " notification was not triggered because alarm is disabled.")
		elif disappear_time < datetime.utcnow() :
			log.info(name + " notification was not triggered because time_left had passed.")
		else:
			log.info(name + " notication was triggered!")
			for alarm in self.alarms:
				alarm.pokemon_alert(pkinfo)
		if len(self.lured_seen) > 10000:
			self.clear_stale(lured=True);

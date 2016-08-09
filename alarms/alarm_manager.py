#Setup Logging
import logging
log = logging.getLogger(__name__)

#Python Utility imports
import os
import json
import time
from datetime import datetime
from threading import Thread

#Local imports
from . import config
from pushbullet_alarm import Pushbullet_Alarm
from slack_alarm import Slack_Alarm
from twilio_alarm import Twilio_Alarm
from telegram_alarm import Telegram_Alarm
from utils import *

class Alarm_Manager(Thread):

	def __init__(self, queue):
		#Intialize as Thread
		super(Alarm_Manager, self).__init__()
		#Import settings from Alarms.json
		filepath = config['ROOT_PATH']
		with open(os.path.join(filepath, 'alarms.json')) as file:
			settings = json.load(file)
			alarm_settings = settings["alarms"]
			self.notify_list = make_notify_list(settings["pokemon"])
			out = ""
			for id in self.notify_list:
				out = out + "{}, ".format(get_pkmn_name(id))
			log.info("You will be notified of the following pokemon: \n" + out[:-2])
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
	
	#Threaded loop to process request data from the queue 
	def run(self):
		log.info("PokeAlarm has started! Your alarms should trigger now.")
		while True:
			for i in range(1000):
				data = self.queue.get(block=True)
				self.queue.task_done()
				if data['type'] == 'pokemon' :
					log.debug("Request processed for #%s" % data['message']['pokemon_id'])
					if data['message']['encounter_id'] not in self.seen:
						self.trigger_pkmn(data['message'])
				elif data['type'] == 'pokestop' : 
					log.debug("Pokestop notifications not yet implimented.")
				elif data['type'] == 'pokegym' :
					log.debug("Pokegym notifications not yet implimented.")
			log.debug("Cleaning up 'seen' set...")
			self.clear_stale();
			
	#Send a notification to alarms about a found pokemon
	def trigger_pkmn(self, pkmn):
		#Mark the pokemon as seen along with exipre time
		dissapear_time = datetime.utcfromtimestamp(pkmn['disappear_time']);
		#Apply optional time fix if selected (Bug correction for PokemonGo-Map)
		if config['TIME_FIX'] :
			dissapear_time = time_fix(pkmn['disappear_time'])
		self.seen[pkmn['encounter_id']] = dissapear_time
		
		#Check if Pokemon is on the notify list
		pkmn_id = pkmn['pokemon_id']
		name = get_pkmn_name(pkmn_id)
		if pkmn_id not in self.notify_list:
			log.info(name + " ignored: notify not enabled.")
			return
		
		#Check if the Pokemon is outside of notify range
		lat = pkmn['latitude']
		lng = pkmn['longitude']
		dist = get_dist([lat, lng])
		if dist >= self.notify_list[pkmn_id]:
			log.info(name + " ignored: outside range")
			log.info(dist)
			log.info(self.notify_list[pkmn_id])
			return
		
		#Check if the Pokemon has already expired
		if dissapear_time < datetime.utcnow() :
			log.info(name + " ignore: time_left has passed.")
			return
			
		#Trigger the notifcations
		log.info(name + " notication was triggered!")
		timestamps = get_timestamps(dissapear_time)
		pkinfo = {
			'id': str(pkmn_id),
 			'pkmn': name,
			'addr': get_address(lat, lng),
			'loc' : "{},{}".format(lat,lng),
			'gmaps': get_gmaps_link(lat, lng),
			'dist': "%dm" % dist,
			'time_left': timestamps[0],
			'12h_time': timestamps[1],
			'24h_time': timestamps[2],
			'dir': get_dir(lat,lng)
			
		}
		
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
			if self.seen[id] < datetime.utcnow() :
				old.append(id)
		for id in old:
			del self.seen[id]
	
	

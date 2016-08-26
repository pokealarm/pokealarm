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
from utils import *

class Alarm_Manager(Thread):

	def __init__(self, queue):
		#Intialize as Thread
		super(Alarm_Manager, self).__init__()
		#Import settings from Alarms.json
		filepath = config['ROOT_PATH']
		with open(os.path.join(filepath, config['CONFIG_FILE'])) as file:
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
						from Pushbullet import Pushbullet_Alarm
						self.alarms.append(Pushbullet_Alarm(alarm))
					elif alarm['type'] == 'pushover' :
						from Pushover import Pushover_Alarm
						self.alarms.append(Pushover_Alarm(alarm))
					elif alarm['type'] == 'slack' :
						from Slack import Slack_Alarm
						self.alarms.append(Slack_Alarm(alarm))
					elif alarm['type'] == 'telegram' :
						from Telegram import Telegram_Alarm
						self.alarms.append(Telegram_Alarm(alarm))
					elif alarm['type'] == 'twilio' :
						from Twilio import Twilio_Alarm
						self.alarms.append(Twilio_Alarm(alarm))
					elif alarm['type'] == 'twitter' :
						from Twitter import Twitter_Alarm
						self.alarms.append(Twitter_Alarm(alarm))
					else:
						log.info("Alarm type not found: " + alarm['type'])
					set_optional_args(str(alarm))
				else:
					log.info("Alarm not activated: " + alarm['type'] + " because value not set to \"True\"")
	
	#Threaded loop to process request data from the queue 
	def run(self):
		log.info("PokeAlarm has started! Your alarms should trigger now.")
		while True:
			for i in range(5000): #Take a break and clean house every 5000 requests handled
				data = self.queue.get(block=True)
				self.queue.task_done()
				if data['type'] == 'pokemon' :
					if 'pokemon_id' not in data['message']:
						log.debug("Invalid pokemon format - ignoring.")
						break
					log.debug("Request processing for #%s" % data['message']['pokemon_id'])
					if data['message']['encounter_id'] not in self.seen:
						self.trigger_pkmn(data['message'])
					log.debug("Finished processing for #%s" % data['message']['pokemon_id'])
				elif data['type'] == 'pokestop' : 
					log.debug("Pokestop notifications not yet implemented.")
				elif data['type'] == 'pokegym' :
					log.debug("Pokegym notifications not yet implemented.")
			log.debug("Cleaning up 'seen' set...")
			self.clear_stale();
			
	#Send a notification to alarms about a found pokemon
	def trigger_pkmn(self, pkmn):
		#Mark the pokemon as seen along with exipre time
		dissapear_time = datetime.utcfromtimestamp(pkmn['disappear_time']);
		self.seen[pkmn['encounter_id']] = dissapear_time
		pkmn_id = pkmn['pokemon_id']
		name = get_pkmn_name(pkmn_id)
		
		#Check if the Pokemon has already expired
		if dissapear_time < datetime.utcnow() :
			log.info(name + " ignore: time_left has passed.")
			return
		
		#Check if Pokemon is on the notify list
		if pkmn_id not in self.notify_list:
			log.info(name + " ignored: notify not enabled.")
			return

		#Check if the Pokemon is outside of notify range
		lat = pkmn['latitude']
		lng = pkmn['longitude']
		dist = get_dist([lat, lng])
		if dist >= self.notify_list[pkmn_id]:
			log.info(name + " ignored: outside range")
			log.debug('Pokemon must be less than {:f}, but was {:f}.'.format(self.notify_list[pkmn_id], dist))
			return
        
		#Check if the Pokemon is in the geofence
		if 'GEOFENCE' in config:
			if config['GEOFENCE'].contains(lat,lng) is not True:
				log.info(name + " ignored: outside geofence")
				return
		#Trigger the notifcations
		log.info(name + " notication was triggered!")
		timestamps = get_timestamps(dissapear_time)
		pkmn_info = {
			'id': str(pkmn_id),
 			'pkmn': name,
			'lat' : "{}".format(repr(lat)),
			'lng' : "{}".format(repr(lng)),
			'gmaps': get_gmaps_link(lat, lng),
			'dist': "%d%s" % (dist, 'yd' if config['UNITS'] == 'imperial' else 'm'),
			'time_left': timestamps[0],
			'12h_time': timestamps[1],
			'24h_time': timestamps[2],
			'dir': get_dir(lat,lng)
		}
		if config['REV_LOC']:
			pkmn_info.update(**reverse_location(pkmn_info))
		if config['DM_WALK']:
			pkmn_info.update(**get_walking_data(pkmn_info))
		if config['DM_BIKE']:
			pkmn_info.update(**get_biking_data(pkmn_info))
		if config['DM_DRIVE']:
			pkmn_info.update(**get_driving_data(pkmn_info))
			
		for alarm in self.alarms:
			alarm.pokemon_alert(pkmn_info)

	#Send a notication about pokemon lure found
	def notify_lures(self, lures):
		raise NotImplementedError("This method is not yet implemented.")
	
	#Send a notifcation about pokemon gym detected
	def notify_gyms(self, gyms):
		raise NotImplementedError("This method is not yet implemented.")
		
	#clear expired pokemon so that the seen set is not too large
	def clear_stale(self):
		old = []
		for id in self.seen:
			if self.seen[id] < datetime.utcnow() :
				old.append(id)
		for id in old:
			del self.seen[id]

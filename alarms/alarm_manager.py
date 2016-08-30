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
		with open(get_path(config['CONFIG_FILE'])) as file:
			settings = json.load(file)
			alarm_settings = settings["alarms"]
			self.notify_list = make_notify_list(settings["pokemon"])
			out = ""
			for id in self.notify_list:
				out = out + "{}, ".format(get_pkmn_name(id))
			log.info("You will be notified of the following pokemon: \n" + out[:-2])
			self.stop_list =  make_pokestops_list(settings["pokestops"])
			self.gym_list = make_gym_list(settings["gyms"])
			self.pokemon, self.pokestops, self.gyms   = {}, {}, {}
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
					log.debug("Request processing for Pokemon #%s" % data['message']['pokemon_id'])
					self.trigger_pokemon(data['message'])
					log.debug("Finished processing for Pokemon #%s" % data['message']['pokemon_id'])
				elif data['type'] == 'pokestop' : 
					log.debug("Request processing for Pokestop %s" % data['message']['pokestop_id'])
					self.trigger_pokestop(data['message'])
					log.debug("Finished processing for Pokestop %s" % data['message']['pokestop_id'])
				elif data['type'] == 'gym' :
					log.debug("Request processing for Gym %s" % data['message']['gym_id'])
					self.trigger_gym(data['message'])
					log.debug("Finished processing for Gym %s" % data['message']['gym_id'])
				else:
					log.debug("Invalid type specified.")
			log.debug("Cleaning up 'seen' sets...")
			self.clear_stale();
			
	#Send a notification to alarms about a found pokemon
	def trigger_pokemon(self, pkmn):
		#If already alerted, skip
		if pkmn['encounter_id'] in self.pokemon:
			return
			
		#Mark the pokemon as seen along with exipre time
		dissapear_time = datetime.utcfromtimestamp(pkmn['disappear_time']);
		self.pokemon[pkmn['encounter_id']] = dissapear_time
		pkmn_id = pkmn['pokemon_id']
		name = get_pkmn_name(pkmn_id)
		
		#Check if the Pokemon has already expired
		seconds_left = (dissapear_time - datetime.utcnow()).total_seconds()
		if seconds_left < config['TIME_LIMIT'] :
			log.info(name + " ignored: not enough time remaining.")
			log.debug("Time left must be %f, but was %f." % (config['TIME_LIMIT'], seconds_left))
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
			log.debug("Pokemon must be less than %d, but was %d." % (self.notify_list[pkmn_id], dist))
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
		pkmn_info = self.optional_arguments(pkmn_info)
			
		for alarm in self.alarms:
			alarm.pokemon_alert(pkmn_info)

	#Send a notication about Pokestop
	def trigger_pokestop(self, stop):
		#Check if stop is lured or not
		if stop['lure_expiration'] is None:
			return
		
		#If Lures are enabled
		if 'lured' not in self.stop_list:
			return
			
		#If already alerted, skip
		id = stop['pokestop_id']
		dissapear_time = datetime.utcfromtimestamp(stop['lure_expiration'])
		if id in self.pokestops and self.pokestops[id] == dissapear_time:
			return
		self.pokestops[id] = dissapear_time
		
		#Check if the Pokestop has already expired
		seconds_left = (dissapear_time - datetime.utcnow()).total_seconds()
		if seconds_left < config['TIME_LIMIT'] :
			log.info("Pokestop ignored: not enough time remaining.")
			log.debug("Time left must be %f, but was %f." % (config['TIME_LIMIT'], seconds_left))
			return
		
		#Check if the Pokestop is outside of notify range
		lat = stop['latitude']
		lng = stop['longitude']
		dist = get_dist([lat, lng])
		if dist >=  self.stop_list['lured']:
			log.info("Pokestop ignored: outside range")
			log.debug("Pokestop must be less than %d, but was %d." % (self.notify_list[pkmn_id], dist))
			return
		
		#Check if the Pokestop is in the geofence
		if 'GEOFENCE' in config:
			if config['GEOFENCE'].contains(lat,lng) is not True:
				log.info("Pokestop ignored: outside geofence")
				return
		
		#Trigger the notifcations
		log.info("Pokestop notication was triggered!")
		timestamps = get_timestamps(dissapear_time)
		stop_info = {
			'id': id,
			'lat' : "{}".format(repr(lat)),
			'lng' : "{}".format(repr(lng)),
			'gmaps': get_gmaps_link(lat, lng),
			'dist': "%d%s" % (dist, 'yd' if config['UNITS'] == 'imperial' else 'm'),
			'time_left': timestamps[0],
			'12h_time': timestamps[1],
			'24h_time': timestamps[2],
			'dir': get_dir(lat,lng)
		}

		stop_info = self.optional_arguments(stop_info)
		
		for alarm in self.alarms:
			alarm.pokestop_alert(stop_info)

	
	#Send a notifcation about pokemon gym detected
	def trigger_gym(self, gym):
		id = gym['gym_id']
		old_team = self.gyms.get(id)
		new_team = gym['team_id'] 	
		self.gyms[id] = new_team
		
		#Check to see if the gym has changed 
		if old_team == None or new_team == old_team:
			log.debug("Gym ignored: no change detected")
			return #ignore neutral for now
		
		#Check for Alert settings
		old_team = get_team_name(old_team)
		new_team = get_team_name(new_team)
		L = [self.gym_list.get("From_%s" % old_team), self.gym_list.get("To_%s" % new_team)]
		min_dist = max((x for x in L if x is not None), -1)
		if min_dist is -1:
			log.info("Gym ignored: alert not set")
			return
			
		#Check if the Gym is outside of notify range
		lat = gym['latitude']
		lng = gym['longitude']
		dist = get_dist([lat, lng])
		if dist >= min_dist:
			log.info("Gym ignored: outside range")
			log.debug("Gym must be less than %d, but was %d." % (self.notify_list[pkmn_id], dist))
			return
		
		#Check if the Gym is in the geofence
		if 'GEOFENCE' in config:
			if config['GEOFENCE'].contains(lat,lng) is not True:
				log.info("Gym ignored: outside geofence")
				return
		
		#Trigger the notifcations
		log.info("Gym notication was triggered!")
		gym_info = {
			'id': id,
			'lat' : "{}".format(repr(lat)),
			'lng' : "{}".format(repr(lng)),
			'gmaps': get_gmaps_link(lat, lng),
			'dist': "%d%s" % (dist, 'yd' if config['UNITS'] == 'imperial' else 'm'),
			'dir': get_dir(lat,lng),
			'points': gym['gym_points'],
			'old_team': old_team,
			'new_team': new_team
		}
		gym_info = self.optional_arguments(gym_info)
		
		for alarm in self.alarms:
			alarm.gym_alert(gym_info)
		
	#clear expired pokemon so that the seen set is not too large
	def clear_stale(self):
		for dict in (self.pokemon, self.pokestops, self.gyms):
			old = []
			for id in dict:
				if dict[id] < datetime.utcnow() :
					old.append(id)
			for id in old:
				del dict[id]
	
	#clear expired pokemon so that the seen set is not too large
	def optional_arguments(self, info):
		if config['REV_LOC']:
			info.update(**reverse_location(info))
		if config['DM_WALK']:
			info.update(**get_walking_data(info))
		if config['DM_BIKE']:
			info.update(**get_biking_data(info))
		if config['DM_DRIVE']:
			info.update(**get_driving_data(info))
		
		return info

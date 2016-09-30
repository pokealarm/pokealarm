#Setup Logging
import logging
log = logging.getLogger(__name__)

#Python Utility imports
import os
import json
import time
import traceback
import threading
import Queue
from datetime import datetime
from threading import Thread

#Local imports
from . import config
from utils import *

class Alarm_Manager(Thread):

	def __init__(self):
		#Intialize as Thread
		super(Alarm_Manager, self).__init__()
		#Import settings from Alarms.json
		with open(get_path(config['CONFIG_FILE'])) as file:
			settings = json.load(file)
			alarm_settings = settings["alarms"]
			self.set_pokemon(settings["pokemon"])
			log.info("The following pokemon are set:")
			for id in sorted(self.pokemon_list.keys()):
				log.info("{name}: max_dist({max_dist}), min_iv({min_iv}), move1({move_1}), move2({move_2})".format(**self.pokemon_list[id]))
			self.stop_list =  make_pokestops_list(settings["pokestops"])
			self.gym_list = make_gym_list(settings["gyms"])
			self.pokemon, self.pokestops, self.gyms = {}, {}, {}
			self.alarms = []
			self.queue = Queue.Queue()
			self.data = {}
			self.lock = threading.Lock()
			for alarm in alarm_settings:
				if alarm['active'] == "True" :
					if alarm['type'] == 'boxcar' :
						from Boxcar import Boxcar_Alarm
						self.alarms.append(Boxcar_Alarm(alarm))
					elif alarm['type'] == 'pushbullet' :
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
	
	#Update this object with a list of pokemon 
	def set_pokemon(self, settings):
		pokemon = {}
		default_dist = float(settings.pop('max_dist', None) or 'inf');
		default_iv = float(settings.pop('min_iv', None) or 0);
		log.info("Pokemon Defaults: max_dist (%.2f) and min_iv (%.2f)" % (default_dist, default_iv))
		for name in settings:
			id = get_pkmn_id(name)
			if id is None:
				log.info("Unable to find pokemon named %s... Skipping." % name )
				continue
			if parse_boolean(settings[name]) == False : #If set to false, skip.
				log.debug("%s name set to 'false'. Skipping... " % name)
				continue
			else:
				try:
					info = settings[name]
					if parse_boolean(info) == True:
						info = {}
					pokemon[id] = {
						"name": get_pkmn_name(id),
						"max_dist": float(info.get('max_dist', None) or default_dist),
						"min_iv": float(info.get('min_iv', None) or default_iv),
						"move_1": info.get("move_1", 'all'),
						"move_2": info.get("move_2", 'all'),
						"prio": info.get("prio", none),
						"pkmn_sound": info.get("pkmn_sound", none)
					}
				except Exception as e: 
					log.debug("%s error has occured trying to set Pokemon %s" % (str(e), id))
		self.pokemon_list = pokemon
	
	#Update data about this request
	def update(self, id, info):
		self.lock.acquire()
		try:
			if id not in self.data:
				self.queue.put(id)
			self.data[id] = info #update info if changed
		finally:
			self.lock.release()
	
	#Threaded loop to process request data from the queue 
	def run(self):
		log.info("PokeAlarm has started! Your alarms should trigger now.")
		while True:
			try:
				count = 0;
				for i in range(5000): #Take a break and clean house every 5000 requests handled
					id = self.queue.get(block=True)
					self.lock.acquire()
					try: #Get id and remove data from the queue
						data = self.data[id]
						del self.data[id]
						self.queue.task_done()
					finally:
						self.lock.release()
					if data['type'] == 'pokemon' :
						log.debug("Request processing for Pokemon #%s" % data['message']['pokemon_id'])
						self.trigger_pokemon(data['message'])
						log.debug("Finished processing for Pokemon #%s" % data['message']['pokemon_id'])
					elif data['type'] == 'pokestop' : 
						log.debug("Request processing for Pokestop %s" % data['message']['pokestop_id'])
						self.trigger_pokestop(data['message'])
						log.debug("Finished processing for Pokestop %s" % data['message']['pokestop_id'])
					elif data['type'] == 'gym' or data['type'] == 'gym_details'  :
						log.debug("Request processing for Gym %s" % data['message'].get('gym_id', data['message'].get('id')))
						self.trigger_gym(data['message'])
						log.debug("Finished processing for Gym %s" % data['message'].get('gym_id', data['message'].get('id')))
					else:
						log.debug("Invalid type specified: %s" % data['type'])
				log.debug("Cleaning up 'seen' sets...")
				self.clear_stale();
			except Exception as e:
				log.error("Error while processing request: %s" % e)
				log.debug("Stack trace: \n {}".format(traceback.format_exc()))
				if data:
					log.debug("Request format: \n %s " % json.dumps(data, indent=4, sort_keys=True))
					
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
		
		#Check if Pokemon has any filters set up
		filter = self.pokemon_list.get(pkmn_id)
		if filter is None:
			log.info(name + " ignored: notify not enabled.")
			return
		
		#Check if the Pokemon has already expired
		seconds_left = (dissapear_time - datetime.utcnow()).total_seconds()
		if seconds_left < config['TIME_LIMIT'] :
			log.info(name + " ignored: not enough time remaining.")
			log.debug("Time left must be %f, but was %f." % (config['TIME_LIMIT'], seconds_left))
			return

		#Check if the Pokemon IV's
		atk = int(pkmn.get('individual_attack') or 0)
		dfs = int(pkmn.get('individual_defense') or 0)
		sta = int(pkmn.get('individual_stamina') or 0)
		iv = float(((atk + dfs + sta)*100)/float(45))
		if filter.get('min_iv') > float(iv):
			log.info("%s ignored: IV was %f (needs to be %f)" % (name, iv, filter.get('min_iv')))
			return
		
		#Check moveset
		move1 = get_pkmn_move(pkmn.get('move_1', "none"))
		move2 = get_pkmn_move(pkmn.get('move_2', "none"))
		if move1 != "unknown" and filter.get('move_1') != 'all' and filter.get('move_1').find(move1) == -1:
			log.info("%s ignored: Incorrect Move_1 (%s)" %(name, move1))
			return
			
		if move2 != "unknown" and filter.get('move_2') != 'all' and filter.get('move_2').find(move2) == -1:
			log.info("%s ignored: Incorrect Move_2 (%s)" %(name, move2))
			return


		#Check if the Pokemon is outside of notify range
		lat = pkmn['latitude']
		lng = pkmn['longitude']
		dist = get_dist([lat, lng])

		if dist >= filter.get('max_dist'):
			log.info(name + " ignored: outside range")
			log.debug("Pokemon must be less than %d, but was %d." % (filter['max_dist'], dist))
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
			'encounter_id': pkmn['encounter_id'],
 			'pkmn': name,
			'lat' : "{}".format(repr(lat)),
			'lng' : "{}".format(repr(lng)),
			'gmaps': get_gmaps_link(lat, lng),
			'dist': "%d%s" % (dist, 'yd' if config['UNITS'] == 'imperial' else 'm'),
			'time_left': timestamps[0],
			'12h_time': timestamps[1],
			'24h_time': timestamps[2],
			'dir': get_dir(lat,lng),
			'move1': str(move1),
			'move2': str(move2),
			'atk': atk,
			'def': dfs,
			'sta': sta,
			'iv': "%.2f" % iv,
			'respawn_text': get_respawn_text(pkmn.get('respawn_info', 0)),
			'prio': str(prio),
			'pkmn_sound': str(pkmn_sound)
		}

		pkmn_info = self.optional_arguments(pkmn_info)
		for alarm in self.alarms:
			alarm.pokemon_alert(pkmn_info)

	#Send a notication about Pokestop
	def trigger_pokestop(self, stop):
		#Check if stop is lured or not
		if stop['lure_expiration'] is None:
			return
		
		#If Lures are not enabled
		if self.stop_list.get('lured') is None:
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
			log.debug("Pokestop must be less than %d, but was %d." % (self.stop_list['lured'], dist))
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
		id = gym.get('gym_id', gym.get('id'))
		old_team = self.gyms.get(id)
		new_team = gym.get('team_id', gym.get('team')) 	
		self.gyms[id] = new_team
		log.debug("Gym %s - %s to %s" % (id, old_team, new_team))
		
		#Check to see if the gym has changed 
		if old_team == None or new_team == old_team:
			log.debug("Gym ignored: no change detected")
			return #ignore neutral for now
		
		#Check for Alert settings
		old_team = get_team_name(old_team)
		new_team = get_team_name(new_team)
		max_dist = max(self.gym_list.get("From_%s" % old_team, -1), self.gym_list.get("To_%s" % new_team, -1))
		if max_dist is -1:
			log.info("Gym ignored: alert not set")
			return
			
		#Check if the Gym is outside of notify range
		lat = gym['latitude']
		lng = gym['longitude']
		dist = get_dist([lat, lng])
		if dist >= max_dist:
			log.info("Gym ignored: outside range")
			log.debug("Gym must be less than %d, but was %d." % (max_dist, dist))
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
			'points': str(gym.get('gym_points')),
			'old_team': old_team,
			'new_team': new_team
		}
		gym_info = self.optional_arguments(gym_info)
		
		for alarm in self.alarms:
			alarm.gym_alert(gym_info)
		
	#clear expired pokemon so that the seen set is not too large
	def clear_stale(self):
		for dict in (self.pokemon, self.pokestops):
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

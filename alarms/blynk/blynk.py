#!/usr/bin/python
# -*- coding: utf-8 -*-
#Setup logging
import logging
log = logging.getLogger(__name__)
#Python Modules
from datetime import datetime
from decimal import *
#Local Modules
from ..alarm import Alarm
from ..utils import *
from urllib2 import Request, urlopen
from urllib2 import HTTPError

class blynk_alarm(Alarm):

	#Gather settings and create alarm
	def __init__(self, settings):
		self.token = settings['api_key']
		self.notification_radius = settings['gps_radius']
		self.id = settings.get('id', "<id>")
		self.addr = settings.get('addr', "<addr>")
		self.time = settings.get('time_left', "<24h_time>")
		self.gmaps = settings.get('gmaps', "<gmaps>")
		self.lat = settings.get('lat', "<lat>")
		self.lng = settings.get('lng', "<lng>")	
	
	def send_blynk(self,pin,value):
		time.sleep(0.761)	
		values = """
		  [
			
			"""+ value +"""
		  ]
		"""		
		headers = {
		  'Content-Type': 'application/json'
		}
		request = Request('http://blynk-cloud.com/'+self.token+'/pin/V'+str(pin)+'', data=values, headers=headers)
		request.get_method = lambda: 'PUT'
		
		try:
			response_body = urlopen(request).read()
			log.info(str(pin))
			log.info(response_body)	

						
		except HTTPError as e:
			log.info(e.read())
			log.info(format(pin),format(value))
	
	
	
	def pokemon_alert(self, pkinfo):
		from decimal import Decimal
		args = {
			'id': replace(self.id, pkinfo),
			'24h_time': replace(self.time, pkinfo),
			'lat': replace(self.lat, pkinfo),
			'lng': replace(self.lng, pkinfo)
		}
		
		gps_file = open("/var/www/html/gps.txt", "r")	
		coord = gps_file.read()
		coords = coord.rpartition(',')
		gps_file.close()
		self.gps_lat = coords[0]
		self.gps_lng = coords[2]			
		log.info(Decimal(self.gps_lat))
		log.info(Decimal(self.gps_lng))		
		log.info("Substrahiert:")
		log.info(Decimal(args['lat']) - Decimal(self.gps_lat))
		log.info(Decimal(args['lng']) - Decimal(self.gps_lng))
		
		
		if (((Decimal(args['lat']) - Decimal(self.gps_lat)) < Decimal(self.notification_radius) and (Decimal(args['lat']) - Decimal(self.gps_lat)) > (Decimal('-1')*Decimal(self.notification_radius))) and ((Decimal(args['lng']) - Decimal(self.gps_lng)) < Decimal(self.notification_radius) and (Decimal(args['lng']) - Decimal(self.gps_lng)) > (Decimal('-1')*Decimal(self.notification_radius)))):
			#### Difference for near radius proximity: (5m) Decimal('0.00005')):
			self.send_blynk(0,args['id'])
			
			###########	CUT THAT COORDINATES###########################					
			lat_string = args['lat']
			lng_string = args['lng']	
			# coordinate getting cut in two figure number because blynk vlaues can only be 255 so cut to mutliple Virtual pins with max 99 and getting assembled back in arduino code
			# probably better to cut them to two figure rgb values which would use less virtual pins but thats more mixed up
			lat_coords =lat_string.rpartition('.')
			lng_coords =lng_string.rpartition('.')			
			pre_point_lat = lat_coords[0]   #V1
			pre_point_lng = lng_coords[0]   #V2
			
			after_point_lat = lat_coords[2] 
			after_point_lng = lng_coords[2]
			
			## if clauses to remove beginning zeros in 2 figure values to avoid blynk error at values like 04 gets set back together in arduino code
			if (after_point_lat[0] == '0'):
				after_point_lat_one = after_point_lat[1]   #V3
			else:
				after_point_lat_one = after_point_lat[0] + after_point_lat[1]#V3
			
			
			if (after_point_lng[0] == '0'):
				after_point_lng_one = after_point_lng[1]   #V4
			else:
				after_point_lng_one = after_point_lng[0] + after_point_lng[1]	#V4		
			######################################################################
			if (after_point_lat[2] == '0'):
				after_point_lat_two = after_point_lat[3]   #V5
			else:
				after_point_lat_two = after_point_lat[2] + after_point_lat[3]#V5
			
			
			if (after_point_lng[2] == '0'):
				after_point_lng_two = after_point_lng[3]   #V6
			else:
				after_point_lng_two = after_point_lng[2] + after_point_lng[3]	#V6			
			###########################################################################
			
			
			# these long delays are to avoid blynk error 500 I got previously. You could try to reduce them for faster time 
			after_point_lat_three = after_point_lat [4] #V7
			after_point_lng_three = after_point_lng [4] #V8

			
			time.sleep(1.643)
			self.send_blynk(1,pre_point_lat)
			self.send_blynk(2,pre_point_lng)
			self.send_blynk(3,after_point_lat_one)
			time.sleep(1.246)
			self.send_blynk(4,after_point_lng_one)
			self.send_blynk(5,after_point_lat_two)
			
			
			time.sleep(0.523)
			self.send_blynk(6,after_point_lng_two)
			time.sleep(1.613)
			self.send_blynk(7,after_point_lat_three)
			self.send_blynk(8,after_point_lng_three)
					
			
			################################################################
			till_time = args['24h_time']
			
			if (till_time[0] == '0'):
				till_hour = till_time[1]   #V9
			else:
				till_hour = till_time[0] + till_time[1]#V9	
			
			if (till_time[3] == '0'):
				till_minute = till_time[4]   #V10
			else:
				till_minute = till_time[3] + till_time[4]#V10	
			
			if (till_time[6] == '0'):
				till_second = till_time[7]   #V10
			else:
				till_second = till_time[6] + till_time[7]#V10					

				
			self.send_blynk(9,till_hour) 	#V9
			time.sleep(1.12)
			self.send_blynk(10,till_minute) #V10
			self.send_blynk(11,till_second) #V11
			
			#debugging halt 
			#time.sleep(1000)
			
			
#Setup Logging
import logging
log = logging.getLogger(__name__)

#Python Modules
import sys
import csv
from sympy.geometry import Point, Polygon
from sympy.core.cache import clear_cache
from urllib import urlencode

from . import config

class Geofence(object):	

	#Takes in a file of coordinates y,x
	def __init__(self, filepath):	
		log.info("Creating geofence...")
		self.polygon = None
		points = []
		with open(filepath) as file:
			rows = csv.reader(file, delimiter=',')
			for row in rows:
				if len(row) != 2:
					log.info("Invalid point specificed: " + row)
					continue
				p = Point(float(row[0]), float(row[1]), evaluate=False)
				points.append(p)
		if len(points) == 2:
			p1 = Point(points[0].x, points[0].y, evaluate=False)
			p2 = Point(points[1].x, points[0].y, evaluate=False)
			p3 = Point(points[1].x, points[1].y, evaluate=False)
			p4 = Point(points[0].x, points[1].y, evaluate=False)
			self.polygon = Polygon(p1, p2, p3, p4)
			log.info(self.polygon)
		elif len(points) > 2:
			self.polygon = Polygon(*points)
		log.debug(self.polygon)
		log.info("Geofence established!")

	#Return true if x,y points are inside geofence
	def contains(self, x, y):
		rtn = self.polygon.encloses_point(Point(x,y, evaluate=False))
		clear_cache()
		return rtn

# Gets the url of a static google map of the currently set geofence and/or location 
def get_geofence_static_map():
	geofence = config.get('GEOFENCE')
	location = config.get('LOCATION')
	api_key = config.get('API_KEY')
	if geofence is None and location is None: # No location or Geofence set
		return False

	url_string = "https://maps.googleapis.com/maps/api/staticmap?size=600x600&maptype=roadmap"

	#Draw polygon
	if geofence is not None:
		poly_string = "color:0x0000ff80|fillcolor:0x00000022|weight:3"
		vert = geofence.polygon.vertices
		for pt_lat, pt_lng in vert:
			poly_string = poly_string + '|{!s},{!s}'.format(float(pt_lat),float(pt_lng))
		poly_string = poly_string + '|{!s},{!s}'.format(float(vert[0][0]), float(vert[0][1])) # Close polygon with first point
		url_string = url_string + '&' + urlencode({'path':poly_string})

	#Draw location marker
	if location is not None:
		marker_string = 'fillcolor:blue|{!s},{!s}'.format(location[0], location[1])
		url_string = url_string + '&' + urlencode({'markers':marker_string})

	#Include API Key if specified
	if api_key is not None:
		url_string = url_string + "&key={}".format(api_key)
	else:
		print "API KEY not provided"

	return url_string


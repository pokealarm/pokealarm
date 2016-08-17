#Setup Logging
import logging
log = logging.getLogger(__name__)

#Python Modules
import sys
import csv
from sympy.geometry import Point, Polygon

class Geofence(object):	

	#Takes in a file of coordinates y,x
	def __init__(self, filepath):	
		self.polygon = None
		points = []
		with open(filepath) as file:
			rows = csv.reader(file, delimiter=',')
			for row in rows:
				log.info("got to here")
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
			self.polygon = Polygon(points)
			log.info(self.polygon)
		log.info("Geofence successfully loaded!")

	#Return true if x,y points are inside geofence
	def contains(self, x, y):
		if self.polygon is not None:
			return self.polygon.encloses_point(Point(x,y))
		else:
			return False

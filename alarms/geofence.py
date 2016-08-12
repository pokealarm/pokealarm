#Setup Logging
import logging
log = logging.getLogger(__name__)

#Python Modules
import sys
import csv
from collections import namedtuple

Point = namedtuple('Point', 'x, y')

class Geofence(object):	
	
	#Takes in a file of coordinates y,x
	def __init__(self, filepath):	
		self.points = []
		with open(filepath) as file:
			rows = csv.reader(file, delimiter=',')
			for row in rows:
				log.info("got to here")
				p = Point(float(row[0]), float(row[1]))
				self.points.append(p)
		log.info("Geofence successfully loaded!")

	#Return true if x,y points are inside geofence
	def contains(self, x, y):
		#If no points, always true
		if self.points is None:
			return true	
			
		inside = False
		prev = self.points[-1]
		for pt in self.points:
			if intersect_seg(x, y, pt, prev):
				inside = not inside
			prev = pt
			
		return inside

_eps = 0.00001
_huge = sys.float_info.max
_tiny = sys.float_info.min

#Returns true if a Point(x,y) would cast a ray that 
#intersects an edge between points a and b
def intersect_seg(x, y, a, b):
    if a.y > b.y:
        a,b = b,a
    if y == a.y or y == b.y:
        p = Pt(x, y + _eps)
 
    intersect = False
 
    if (y > b.y or y < a.y) or (
        x > max(a.x, b.x)):
        return False
 
    if x < min(a.x, b.x):
        intersect = True
    else:
        if abs(a.x - b.x) > _tiny:
            m_red = (b.y - a.y) / float(b.x - a.x)
        else:
            m_red = _huge
        if abs(a.x - x) > _tiny:
            m_blue = (y - a.y) / float(x - a.x)
        else:
            m_blue = _huge
        intersect = m_blue >= m_red
    return intersect

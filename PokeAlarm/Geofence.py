# Standard Library Imports
import re
import logging
import sys
import traceback
from collections import OrderedDict
# 3rd Party Imports
# Local Imports


log = logging.getLogger('Geofence')


# Load in a geofence file
def load_geofence_file(file_path):
    try:
        geofences = OrderedDict()
        name_pattern = re.compile("(?<=\[)([^]]+)(?=\])")
        coor_patter = re.compile("[-+]?[0-9]*\.?[0-9]*"
                                 + "[ \t]*,[ \t]*" + "[-+]?[0-9]*\.?[0-9]*")
        with open(file_path, 'r') as f:
            lines = f.read().splitlines()
        name = "geofence"
        points = []
        for line in lines:
            line = line.strip()
            match_name = name_pattern.search(line)
            if match_name:
                if len(points) > 0:
                    geofences[name] = Geofence(name, points)
                    log.info("Geofence {} added.".format(name))
                    points = []
                name = match_name.group(0)
            elif coor_patter.match(line):
                lat, lng = map(float, line.split(","))
                points.append([lat, lng])
            else:
                log.error("Geofence was unable to parse this line: "
                          + "  {}".format(line))
                log.error("All lines should be either '[name]' or 'lat,lng'.")
                sys.exit(1)
        geofences[name] = Geofence(name, points)
        log.info("Geofence {} added!".format(name))
        return geofences
    except IOError as e:
        log.error("IOError: Please make sure a file with read/write "
                  + "permissions exist at {}".format(file_path))
    except Exception as e:
        log.error("Encountered error while loading Geofence: "
                  + "{}: {}".format(type(e).__name__, e))
    log.debug("Stack trace: \n {}".format(traceback.format_exc()))
    sys.exit(1)


# Geofence object used to determine if points are in a defined range
class Geofence(object):

    # Initialize the Geofence from a given name and a list of points.
    def __init__(self, name, points):
        self.__name = name
        self.__points = points

        self.__min_x = points[0][0]
        self.__max_x = points[0][0]
        self.__min_y = points[0][1]
        self.__max_y = points[0][1]

        for p in points:
            self.__min_x = min(p[0], self.__min_x)
            self.__max_x = max(p[0], self.__max_x)
            self.__min_y = min(p[1], self.__min_y)
            self.__max_y = max(p[1], self.__max_y)

    # Returns True if the point at the given X, Y
    # is inside the polygon, else false
    def contains(self, x, y):
        # Quick check the boundary box of the entire polygon
        if self.__max_x < x or x < self.__min_x \
                or self.__max_y < y or y < self.__min_y:
            return False

        # If it is inside the boundary box, use a raycast
        # from the line and toggle for every edge it hits
        inside = False
        p1x, p1y = self.__points[0]
        n = len(self.__points)
        for i in range(1, n + 1):
            p2x, p2y = self.__points[i % n]
            if min(p1y, p2y) < y <= max(p1y, p2y) and x <= max(p1x, p2x):
                if p1y != p2y:
                    xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                if p1x == p2x or x <= xinters:
                    inside = not inside
            p1x, p1y = p2x, p2y
        return inside

    # Returns the name of this geofence
    def get_name(self):
        return self.__name

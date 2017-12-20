# Standard Library Imports
import re
import logging
import sys
import traceback
# 3rd Party Imports
# Local Imports

log = logging.getLogger('Gymlist')


# Load in a geofence file
def load_gymlist_file(file_path, cache_obj):
    #print file_path
    log.info("Loading Gymlist from file at %s",file_path)
    try:
        gymlist = [] 
        name_pattern = re.compile("(.Friendly.Name.City.Latitude.Long)")
        with open(file_path, 'r') as f:
            lines = f.read().splitlines()
        name = "gymlist"
        gyms = []
        for line in lines:
            line = line.strip()
            match_name = name_pattern.search(line)
            if match_name:
                log.debug("Header: %s",line)
            else:
                b64_id,rm_id,gym_name,gym_lat,gym_lon = line.split(',')
                log.debug("Gym Loaded: %s",gym_name)
                cache_obj.update_gym_info(b64_id, gym_name, " ", " ")
                gyms.append([gym_name,gym_lat,gym_lon])
            #log.debug("Line = {}",line)
            #print line
        log.debug("%s",gyms)
        gymlist.append(Gymlist(name, gyms))
        return gymlist
    except IOError as e:
        log.error("IOError: Please make sure a file with read/write permissions exsist at {}".format(file_path))
    except Exception as e:
        log.error("Encountered error while loading Gymlist: {}: {}".format(type(e).__name__, e))
    log.debug("Stack trace: \n {}".format(traceback.format_exc()))
    sys.exit(1)
    
# Load in a geofence file
def load_gymexclusion_file(file_path):
    print file_path
    try:
        gymexlist = None
        name_pattern = re.compile("(.Friendly.Name.City.Latitude.Long)")
        with open(file_path, 'r') as f:
            lines = f.read().splitlines()
        name = "gymlist"
        gyms = []
        for line in lines:
            line = line.strip()
            match_name = name_pattern.search(line)
            if match_name:
                log.debug("Header: %s",line)
            else:
                f_name,city,g_lat,g_lon,x = line.split(',')
                log.debug("%s,%s,%s,%s",f_name,city,g_lat,g_lon)
                gyms.append([f_name,g_lat,g_lon])
        log.debug("%s",gyms)
        gymexlist = Gymlist(name, gyms)
        return gymexlist
    except IOError as e:
        log.error("IOError: Please make sure a file with read/write permissions exsist at {}".format(file_path))
    except Exception as e:
        log.error("Encountered error while loading Geofence: {}: {}".format(type(e).__name__, e))
    log.debug("Stack trace: \n {}".format(traceback.format_exc()))
    sys.exit(1)


# Geofence object used to determine if points are in a defined range
class Gymlist(object):

    # Initialize the Geofence from a given name and a list of points.
    def __init__(self, name, gyms):
        log.debug("Creating Gymlist object with %s",gyms)
        self.__name = name
        self.__gyms = gyms

    def in_list(self, lat, lon):
        log.debug("Checking for gym location using key: %s,%s",lat, lon)
        for i, sublist in enumerate(self.__gyms):
            if str(lat) in sublist and str(lon) in sublist:
                log.debug("Returning: %d",i)
                return i
        return -1

    def get_gym_info(self, index):
        f_name, city, lat, lon = self.__gyms[index]
        return f_name,city,lat,lon
    # Returns the name of this geofence
    def get_name(self):
        return self.__name
    
class Gymexclusionlist(object):
    # Initialize the Geofence from a given name and a list of points.
    def __init__(self, name, gyms):
        log.debug("Creating Gymexclusionlist object with %s",gyms)
        self.__name = name
        self.__exgems = gyms
        
    def is_gym_excluded(self, value):
        log.debug("Checking gym exclusion using key: %s",value)
        for i, sublist in enumerate(self.__exgems):
            if value in sublist:
                return i
        return -1
    # Returns the name of this geofence
    def get_name(self):
        return self.__name

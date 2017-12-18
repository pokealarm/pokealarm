# Standard Library Imports
import re
import logging
import sys
import traceback
# 3rd Party Imports
# Local Imports

log = logging.getLogger('Rolelist')


# Load in a geofence file
def load_rolelist_file(file_path):
    #print file_path
    log.info("Loading Roleslist from file at %s",file_path)
    try:
        rolelist = []
        with open(file_path, 'r') as f:
            lines = f.read().splitlines()
        name = "rolelist"
        roles = []
        for line in lines:
            line = line.strip()
            role_id,role_city = line.split(',')
            log.debug("Role Loaded: %s",role_city)
            log.debug("Role: %s,%s",role_id,role_city)
            roles.append([role_id,role_city])
        log.debug("%s",roles)
        rolelist.append(Rolelist(role_city,roles))
        return rolelist
    except IOError as e:
        log.error("IOError: Please make sure a file with read/write permissions exsist at {}".format(file_path))
    except Exception as e:
        log.error("Encountered error while loading Rolelist: {}: {}".format(type(e).__name__, e))
    log.debug("Stack trace: \n {}".format(traceback.format_exc()))
    sys.exit(1)

# Geofence object used to determine if points are in a defined range
class Rolelist(object):

    # Initialize the Geofence from a given name and a list of points.
    def __init__(self, role_name, roles):
        log.debug("Creating Gymlist object with %s",roles)
        self.__name = role_name
        self.__roles = roles

    def in_list(self, city):
        log.info("Checking for Role using key: %s",city)
        for i, sublist in enumerate(self.__roles):
            if city in sublist:
                return i
        return -1

    def get_role_id(self, index):
        role_id, role_city = self.__roles[index]
        return role_id


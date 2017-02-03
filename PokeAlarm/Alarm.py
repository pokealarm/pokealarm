# This is a basic interface for the Alarms Modules to implement

# Standard Library Imports
import time
# 3rd Party Imports
# Local Imports
from Utils import parse_boolean

#####################################################  ATTENTION!  #####################################################
# You DO NOT NEED to edit this file to custimize messages for services! Please see the Wiki on the correct way to
# custimize services In fact, doing so will likely NOT work correctly with many features included in PokeAlarm.
#                               PLEASE ONLY EDIT IF YOU KNOW WHAT YOU ARE DOING!
#####################################################  ATTENTION!  #####################################################


class Alarm(object):

    _defaults = {
        "pokemon": {},
        "lures": {},
        "gyms": {}
    }

    # Gather settings and create alarm
    def __init__(self):
        raise NotImplementedError("This is an abstract method.")

    # (Re)establishes Service connection
    def connect(self):
        raise NotImplementedError("This is an abstract method.")

    # Set the appropriate settings for each alert
    def set_alert(self, settings):
        raise NotImplementedError("This is an abstract method.")

    # Send Alert to the Service
    def send_alert(self, alert_settings, info):
        raise NotImplementedError("This is an abstract method.")

    # Trigger an alert based on Pokemon info
    def pokemon_alert(self, pokemon_info):
        raise NotImplementedError("This is an abstract method.")

    # Trigger an alert based on PokeLure info
    def pokestop_alert(self, pokelure_info):
        raise NotImplementedError("This is an abstract method.")

    # Trigger an alert based on PokeGym info
    def gym_alert(self, pokegym_info):
        raise NotImplementedError("This is an abstract method.")

    # Return a version of the string with the correct substitutions made
    @staticmethod
    def replace(string, pkinfo):
        s = string.encode('utf-8')
        for key in pkinfo:
            s = s.replace("<{}>".format(key), str(pkinfo[key]))
        return s

    # Attempts to send the alert with the specified args, reconnecting if neccesary
    @staticmethod
    def try_sending(alarm_log, reconnect, name, send_alert, args):
        for i in range(1, 6):
            try:
                send_alert(**args)
                if i is not 1:
                    alarm_log.info("%s successly reconnected." % name)
                return  # message sent succesfull
            except Exception as e:
                alarm_log.error(e)
                alarm_log.error("%s is having connection issues. %d attempt of 5." % (name, i))
                time.sleep(5)
                reconnect()
        alarm_log.error("Could not connect to %s... Giving up." % name)

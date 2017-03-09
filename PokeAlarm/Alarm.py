# This is a basic interface for the Alarms Modules to implement

# Standard Library Imports
import time
import traceback
# 3rd Party Imports
# Local Imports
from Utils import parse_boolean

#####################################################  ATTENTION!  #####################################################
# You DO NOT NEED to edit this file to custimize messages for services! Please see the Wiki on the correct way to
# custimize services In fact, doing so will likely NOT work correctly with many features included in PokeAlarm.
#                               PLEASE ONLY EDIT IF YOU KNOW WHAT YOU ARE DOING!
#####################################################  ATTENTION!  #####################################################


class Alarm(object):

    _defaults = {  # These are the default values for the 'Alerts'
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

    # (Re)establishes Service connection
    def startup_message(self):
        raise NotImplementedError("This is an abstract method.")

    # Set the appropriate settings for each alert
    def create_alert_settings(self, settings, default):
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
    def try_sending(log, reconnect, name, send_alert, args):
        for i in range(5):
            try:
                send_alert(**args)
                return  # message sent successfully
            except Exception as e:
                log.error("Encountered error while sending notification ({}: {})".format(type(e).__name__, e))
                log.debug("Stack trace: \n {}".format(traceback.format_exc()))
                log.info("{} is having connection issues. {} attempt of 5.".format(name, i+1))
                time.sleep(3)
                reconnect()
        log.error("Could not send notification... Giving up.")

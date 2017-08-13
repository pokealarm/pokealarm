# Standard Library Imports
import time
import traceback
# 3rd Party Imports
# Local Imports

#####################################################  ATTENTION!  #####################################################
# You DO NOT NEED to edit this file to customize messages for services! Please see the Wiki on the correct way to
# customize services In fact, doing so will likely NOT work correctly with many features included in PokeAlarm.
#                               PLEASE ONLY EDIT IF YOU KNOW WHAT YOU ARE DOING!
#####################################################  ATTENTION!  #####################################################


# This is a basic interface for the Alarms Modules to implement
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

    # Trigger an alert when a raid egg has spawned (UPCOMING raid event)
    def raid_egg_alert(self, pokeraid_info):
        raise NotImplementedError("Raid Egg is not implemented!")

    # Trigger an alert when a raid egg is HATCHED (active raid)
    def raid_alert(self, pokeraid_info):
        raise NotImplementedError('Raid Alert is not implemented.')

    # Return a version of the string with the correct substitutions made
    @staticmethod
    def replace(string, pkinfo):
        if string is None:
            return None

        s = string.encode('utf-8')
        for key in pkinfo:
            s = s.replace("<{}>".format(key), str(pkinfo[key]))
        return s

    # Attempts to send the alert with the specified args, reconnecting if neccesary
    @staticmethod
    def try_sending(log, reconnect, name, send_alert, args, max_attempts=3):
        for i in range(max_attempts):
            try:
                send_alert(**args)
                return  # message sent successfully
            except Exception as e:
                log.error("Encountered error while sending notification ({}: {})".format(type(e).__name__, e))
                log.debug("Stack trace: \n {}".format(traceback.format_exc()))
                log.info("{} is having connection issues. {} attempt of {}.".format(name, i+1, max_attempts))
                time.sleep(3)
                reconnect()
        log.error("Could not send notification... Giving up.")

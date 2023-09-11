# Standard Library Imports
import time
import traceback
import re

# 3rd Party Imports
# Local Imports

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ATTENTION! !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#             ONLY EDIT THIS FILE IF YOU KNOW WHAT YOU ARE DOING!
# You DO NOT NEED to edit this file to customize messages! Please ONLY EDIT the
#     the 'alarms.json'. Failing to do so can cause other feature to break!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ATTENTION! !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


# This is a basic interface for the Alarms Modules to implement
class Alarm(object):

    _defaults = {  # These are the default values for the 'Alerts'
        "pokemon": {},
        "lures": {},
        "gyms": {},
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
        raise NotImplementedError("Raid Alert is not implemented.")

    # Trigger an alert when the weather has changed for an s2 cell
    def weather_alert(self, pokeweather_info):
        raise NotImplementedError("Weather Alert is not implemented.")

    # Trigger an alert when a quest is reported
    def quest_alert(self, pokequest_info):
        raise NotImplementedError("Quest Alert is not implemented.")

    # Trigger an alert when a Pokestop is invaded
    def invasion_alert(self, invasion_info):
        raise NotImplementedError("Invasion Alert is not implemented.")

    # Return a version of the string with the correct substitutions made
    @staticmethod
    def replace(string, pkinfo):
        if string is None:
            return None

        return re.sub(
            r"<([^<>\n]+)>",
            lambda m: str(pkinfo.get(m.group(1), f"<{m.group(1)}>")),
            string,
        )

    @staticmethod
    def pop_type(data, param_name, kind, default=None):
        """Pops a parameter as a certain type."""
        try:
            value = data.pop(param_name, default)
            return kind(value)
        except Exception:
            raise ValueError(
                f"Unable to interpret the value '{value}' as a valid {kind} for parameter {param_name}."
            )

    # Attempts to send the alert multiple times
    @staticmethod
    def try_sending(log, reconnect, name, send_alert, args, max_attempts=3):
        for i in range(max_attempts):
            try:
                send_alert(**args)
                return  # message sent successfully
            except Exception as e:
                log.error(
                    "Encountered error while sending notification (%s: %s)",
                    type(e).__name__,
                    e,
                )
                log.debug("Stack trace: \n %s", traceback.format_exc())
                log.info(
                    "%s is having connection issues. %s attempt of %s.",
                    name,
                    i + 1,
                    max_attempts,
                )
                time.sleep(3)
                reconnect()
        log.error("Could not send notification... Giving up.")

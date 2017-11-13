import requests
import logging
import time
import sys
import json
import re

logging.basicConfig(format='%(asctime)s [%(processName)15.15s][%(name)10.10s][%(levelname)8.8s] %(message)s',
                    level=logging.INFO)

log = logging.getLogger('Server')

truthy = frozenset([
    "yes", "Yes", "y", "Y", "true", "True", "TRUE", "YES", "1", "!0"
])

whtypes = {
    "1": "pokemon",
    "2": "pokestop",
    "3": "gym",
    "4": "egg",
    "5": "raid"
}

teams = {
    "0": "Uncontested",
    "1": "Mystic",
    "2": "Valor",
    "3": "Instinct"
}

teams_formatted = re.sub('[{}",]', '', json.dumps(teams, indent=4, sort_keys=True))


def set_init(webhook_type):
    payloadr = {}
    if webhook_type == whtypes["1"]:
        payloadr = {
            "type": "pokemon",
            "message": {
                "pokemon_id": 149,
                "pokemon_level": 30,
                "player_level": 30,
                "latitude": 33.980823,
                "longitude": -81.052988,
                "encounter_id": 0,
                "cp_multiplier": 0.7317000031471252,
                "form": 15,
                "cp": 768,
                "individual_attack": 10,
                "individual_defense": 1,
                "individual_stamina": 9,
                "move_1": 281,
                "move_2": 133,
                "height": 0.5694651007652283,
                "weight": 5.733094215393066,
                "gender": 3,
                "seconds_until_despawn": 1754,
                "spawn_start": 2153,
                "spawn_end": 3264,
                "verified": False
            }
        }
    elif webhook_type == whtypes["2"]:
        payloadr = {
            "type": "pokestop",
            "message": {
                "pokestop_id": 0,
                "enabled": "True",
                "latitude": 62.790967,
                "longitude":  76.927920,
                "active_fort_modifier": 0
            }
        }
    elif webhook_type == whtypes["3"]:
        payloadr = {
            "type": "gym",
            "message": {
                "raid_active_until": 0,
                "gym_id": 0,
                "team_id": 3,
                "guard_pokemon_id": 0,
                # "gym_points": 100,
                "slots_available": 0,
                "guard_pokemon_id": 99,
                "lowest_pokemon_motivation": 0.8795773983001709,
                "total_cp": 11099,
                "enabled": "True",
                "latitude": 62.790967,
                "longitude":  76.927920
            }
        }
    elif webhook_type == whtypes["4"]:
        payloadr = {
            "type": "raid",
            "message": {
                "gym_id": 0,
                "level": 5,
                "latitude": 12.345678,
                "longitude": 12.345678
            }
        }
    elif webhook_type == whtypes["5"]:
        payloadr = {
            "type": "raid",
            "message": {
                "gym_id": 0,
                "pokemon_id": 150,
                "cp": 12345,
                "move_1": 123,
                "move_2": 123,
                "level": 5,
                "latitude": 12.345678,
                "longitude": 12.345678
            }
        }

    return payloadr


def check_int(questionable_input, default):
    if questionable_input.isdigit():
        return int(questionable_input.lstrip("-"))
    else:
        log.info("Not a valid number. Defaulting to " + default)
        return default


def int_or_default(input_parm):
    payload["message"][input_parm] = check_int(raw_input(), payload["message"][input_parm])


def reset_timers():
    current_time = time.time()
    if payload["type"] == "pokemon":
        payload["message"].update({
            "disappear_time": current_time + 10,
            "last_modified_time": current_time,
            "time_until_hidden_ms": 10000
        })
    elif payload["type"] == "pokestop":
        payload["message"].update({
            "last_modified_time": current_time,
            "lure_expiration": current_time + 60,
        })
    elif payload["type"] == "gym":
        payload["message"].update({
            "last_modified": current_time,
            "occupied_since": current_time - 9000
        })
    elif payload["type"] == "raid":
        payload["message"].update({
            "start": current_time + 20,
            "end": current_time + 20 + 60,
        })


def get_and_validate_team():
    team = teams.get(raw_input(), 5)
    if team == 5:
        log.info("Team invalid, defaulting to Uncontested")
        team = 0
    else:
        for team_id, team_name in teams.iteritems():
            if team_name == team:
                team = int(team_id)
    payload["message"]["team_id"] = team


webhooks_formatted = re.sub('[{}",]', '', json.dumps(whtypes, indent=4, sort_keys=True))
print "What kind of webhook would you like to send?(put in a number)\n"+webhooks_formatted+">",
type = whtypes.get(raw_input(), 0)
if type == 0:
    log.error("Must put in valid webhook type")
    sys.exit(1)

payload = set_init(type)

print "What is the URL of where you would like to send the webhook? (default: 127.0.0.1:4000)\n>",
url = raw_input()
if url == '' or url.isspace():
    url = "http://127.0.0.1:4000"
    log.info("Assuming " + url + " as webhook URL")

print "Does location matter?\n>",
if raw_input() in truthy:
    print "Enter latitude\n>",
    latitude = raw_input()
    print "Enter longitude\n>",
    longitude = raw_input()

if type == whtypes["1"]:
    print "Enter Pokemon ID\n>",
    int_or_default("pokemon_id")
    print "Gender (1-3)\n>",
    int_or_default("gender")
    print "Encounters enabled?\n>",
    if raw_input() in truthy:
        print "CP?\n>",
        int_or_default("cp")
        print "Attack IV\n>",
        int_or_default("individual_attack")
        print "Defense IV\n>",
        int_or_default("individual_defense")
        print "Stamina IV\n>",
        int_or_default("individual_stamina")
        print "Id of move 1\n>",
        int_or_default("move_1")
        print "Id of move 2\n>",
        int_or_default("move_2")
elif type == whtypes["3"]:
    print "Which team?(put in a number)\n" + teams_formatted + "\n>",
    get_and_validate_team()
elif type == whtypes["4"]:
    print "What level of gym egg? (1-5)\n>",
    egglevel = check_int(raw_input(), payload["message"]["level"])
    if 6 > egglevel > 0:
        payload["message"]["level"] = egglevel
    else:
        log.info("Egg level invalid. Assuming level 5")
elif type == whtypes["5"]:
    print "Enter pokemon id for raid\n>",
    int_or_default("pokemon_id")
    print "Moveset important?\n>",
    if raw_input() in truthy:
        print "Id of move 1\n>",
        int_or_default("move_1")
        print "Id of move 2\n>",
        int_or_default("move_2")


reset_timers()

while True:
    for i in range(3):
        resp = requests.post(url, json=payload, timeout=5)
        if resp.ok is True:
            # log.info("Notification successful (returned {})".format(resp.status_code))
            print "Notification successful. Returned code {}".format(resp.status_code)
            break
        else:
            log.info("Discord response was {}".format(resp.content))
            raise requests.exceptions.RequestException(
                "Response received {}, webhook not accepted.".format(resp.status_code))
            log.info("Attempting connection again")
    print "Send again?\n>",
    if raw_input() not in truthy:
        break
    if payload["type"] == "pokemon":
        payload["message"]["encounter_id"] += 1
    elif payload["type"] == "gym":
        print "Which gym? (put in number)" + teams_formatted + "\n>",
        get_and_validate_team()
    elif payload["type"] == "raid":
        payload["message"]["gym_id"] += 1
    reset_timers()

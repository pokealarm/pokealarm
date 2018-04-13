import requests
import time
import sys
import json
import re
import os
import portalocker
import pickle
from glob import glob


def get_path(path):
    path = os.path.join(ROOT_PATH, path)
    if not os.path.exists(path):
        print 'The webhook_test.py file has moved from the PokeAlarm/tools' + \
              ' folder!\nPlease put it back or re-download PokeAlarm.'
        sys.exit(1)
    return path


truthy = frozenset([
    "yes", "Yes", "y", "Y", "true", "True", "TRUE", "YES", "1", "!0"
])

whtypes = {
    "1": "pokemon",
    "2": "pokestop",
    "3": "gym",
    "4": "egg",
    "5": "raid",
    "6": "weather"
}

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
locales_file = glob(get_path('../locales/en.json'))[0]
data = json.loads(open(locales_file, 'rb+').read())

teams_formatted = re.sub(
    '[{}",]', '', json.dumps(data['teams'], indent=2, sort_keys=True))

weather_formatted = re.sub(
    '[{}",]', '', json.dumps(data['weather'], indent=2, sort_keys=True))

severity_formatted = re.sub(
    '[{}",]', '', json.dumps(data['severity'], indent=2, sort_keys=True))

day_or_night_formatted = re.sub(
    '[{}",]', '', json.dumps(data['day_or_night'], indent=2, sort_keys=True))

_cache = {}

_gym_info = {}


def set_init(webhook_type):
    payloadr = {}
    current_time = time.time()
    if webhook_type == whtypes["1"]:
        payloadr = {
            "type": "pokemon",
            "message": {
                "pokemon_id": 149,
                "pokemon_level": None,
                "player_level": None,
                "latitude": 37.7876146,
                "longitude": -122.390624,
                "encounter_id": current_time,
                "cp_multiplier": 0.7317000031471252,
                "form": None,
                "cp": None,
                "individual_attack": None,
                "individual_defense": None,
                "individual_stamina": None,
                "move_1": None,
                "move_2": None,
                "height": 0.5694651007652283,
                "weight": None,
                "gender": 3,
                "seconds_until_despawn": 1754,
                "spawn_start": 2153,
                "spawn_end": 3264,
                "verified": False,
                "weather": None,
                "boosted_weather": None
            }
        }
    elif webhook_type == whtypes["2"]:
        payloadr = {
            "type": "pokestop",
            "message": {
                "pokestop_id": current_time,
                "enabled": "True",
                "latitude": 37.7876146,
                "longitude": -122.390624,
                "active_fort_modifier": 0
            }
        }
    elif webhook_type == whtypes["3"]:
        payloadr = {
            "type": "gym",
            "message": {
                "raid_active_until": 0,
                "gym_id": current_time,
                "gym_name": "unknown",
                "team_id": 3,
                "slots_available": 0,
                "guard_pokemon_id": 99,
                "lowest_pokemon_motivation": 0.8795773983001709,
                "total_cp": 11099,
                "enabled": "True",
                "latitude": 37.7876146,
                "longitude": -122.390624
            }
        }
    elif webhook_type == whtypes["4"]:
        payloadr = {
            "type": "raid",
            "message": {
                "gym_id": current_time,
                "gym_name": "unknown",
                "level": 5,
                "latitude": 37.7876146,
                "longitude": -122.390624
            }
        }
    elif webhook_type == whtypes["5"]:
        payloadr = {
            "type": "raid",
            "message": {
                "gym_id": current_time,
                "gym_name": "unknown",
                "pokemon_id": 150,
                "cp": 12345,
                "move_1": 123,
                "move_2": 123,
                "level": 5,
                "latitude": 37.7876146,
                "longitude": -122.390624,
                "weather": 0
            }
        }
    elif webhook_type == whtypes["6"]:
        payloadr = {
            "type": "weather",
            "message": {
                "s2_cell_id": current_time,
                "latitude": 37.7876146,
                "longitude": -122.390624,
                "gameplay_weather": 0,
                "severity": 0,
                "world_time": 1
            }
        }

    return payloadr


def check_int(questionable_input, default):
    if questionable_input.isdigit():
        return int(questionable_input.lstrip("-"))
    else:
        print "Not a valid number. Defaulting to " + str(default)
        return default


def int_or_default(input_parm):
    payload["message"][input_parm] = check_int(
        raw_input(), payload["message"][input_parm])


def get_gym_info(gym_id):
    """ Gets the information about the gym. """
    return _gym_info.get(gym_id, 'unknown')


def gym_or_invalid(prm, prm2):
    questionable_input = raw_input()
    while get_gym_info(questionable_input) == "unknown":
        print "Not a valid gym. Please try again..\n>",
        questionable_input = raw_input()
    print "Gym found! {}".format(get_gym_info(questionable_input))
    payload["message"][prm] = questionable_input
    payload["message"][prm2] = get_gym_info(questionable_input)


def cache_or_invalid():
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input = raw_input()
    if os.path.exists(os.path.join(path, "cache", "{}.cache".format(input))):
        file = os.path.join(path, "cache", "{}.cache".format(input))
        print "Valid file = {}".format(file)
    elif os.path.exists(os.path.join(path, "cache", "manager_0.cache")):
        file = os.path.join(path, "cache", "manager_0.cache")
        print "Invalid file using default = {}".format(file)
    else:
        print "No valid cache file found, terminating.."
        sys.exit(1)
    load_cache(file)


def load_cache(file):
    global _gym_info
    with portalocker.Lock(file, mode="rb") as f:
        data = pickle.load(f)
        _gym_info = data.get('gym_name', {})


def list_cache():
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print "Here is a list of cache files found in \cache\ :"
    for file in os.listdir(os.path.join(path, "cache")):
        if file.endswith(".cache"):
            print file


def list_gyms():
    path = os.path.dirname(os.path.abspath(__file__))
    if len(_gym_info) > 50:
        with portalocker.Lock(os.path.join(path, "gyms.txt"), mode="wb+") as f:
            i = 0
            for key, name in _gym_info.items():
                i += 1
                f.write("[{}] {} : {} \n".format(i, name, key))
            f.close()
        print "Find list of gyms in your \\tools\ folder (gyms.txt)"
        print "Enter gym id for raid (from file)\n>",
    else:
        print "Here is a list of gyms found in your cache:"
        i = 0
        for key, name in _gym_info.items():
            i += 1
            print "[{}] {} : {} ".format(i, name, key)
        print "Enter gym id for raid (from above)\n>",


def gym_cache():
    print "Do you use file caching or does 'gym name' matter? (Y/N)\n>",
    if raw_input() in truthy:
        list_cache()
        print "Enter cache file name to verify the gym (default:manager_0)\n>",
        cache_or_invalid()
        list_gyms()
        gym_or_invalid("gym_id", "gym_name")


def reset_timers_and_encounters():
    current_time = time.time()
    if payload["type"] == "pokemon":
        payload["message"].update({
            "disappear_time": current_time + 10,
            "last_modified_time": current_time,
            "time_until_hidden_ms": 10000,
            "encounter_id": current_time
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
            "gym_id": current_time,
            "start": current_time + 20,
            "end": current_time + 20 + 60,
        })


def get_and_validate_team():
    team = data['teams'].get(raw_input(), 5)
    if team == 5:
        print "Team invalid, defaulting to Neutral"
        team = 0
    else:
        for team_id, team_name in data['teams'].iteritems():
            if team_name == team:
                team = int(team_id)
                break
    payload["message"]["team_id"] = team


webhooks_formatted = re.sub('[{}",]', '', json.dumps(
    whtypes, indent=2, sort_keys=True))
print "What kind of webhook would you like to send?(put in a number)\n"\
      + webhooks_formatted + ">",
type = whtypes.get(raw_input(), 0)
if type == 0:
    print "Must put in valid webhook type"
    sys.exit(1)

payload = set_init(type)

print "What is the URL of where you would like to send the webhook? " \
      + "(default: http://127.0.0.1:4000)\n>",
url = raw_input()
if url == '' or url.isspace():
    url = "http://127.0.0.1:4000"
    print "Assuming " + url + " as webhook URL"

print "Does location matter or do you use geofences? (Y/N)\n>",
if raw_input() in truthy:
    regex_coordinates = re.compile("[-+]?[0-9]*\.?[0-9]*"
                                   + "[ \t]*,[ \t]*" + "[-+]?[0-9]*\.?[0-9]*")
    print "Enter latitude,longitude (Ex. 37.7876146,-122.390624)\n>",
    coordinates = raw_input()
    lat = payload["message"]["latitude"]
    lng = payload["message"]["longitude"]
    if not regex_coordinates.match(coordinates):
        print "Coordinates not valid. Defaulting to " \
              + str(lat) + ',' + str(lng)
    else:
        lat, lng = map(float, coordinates.split(","))
    payload["message"]["latitude"] = lat
    payload["message"]["longitude"] = lng

if type == whtypes["1"]:
    print "Enter Pokemon ID\n>",
    int_or_default("pokemon_id")
    print "Gender (1-3)\n>",
    int_or_default("gender")
    monster_id = "{:03d}".format(payload["message"]["pokemon_id"])
    if monster_id in data['forms'].keys():
        sorted_forms = sorted(data['forms'][monster_id])
        default_form_id = next(iter(sorted_forms))
        forms_formatted = ', '.join(data['forms'][monster_id][x]
                                    for x in sorted_forms)
        print "Which form of " + \
              data["pokemon"][monster_id] + ' would you like? (default: ' + \
              data['forms'][monster_id][default_form_id] + ')\n' + \
              forms_formatted + '\n>',
        form_character = raw_input().lower()
        found = False
        for key, x in data['forms'][monster_id].items():
            if x.lower() == form_character:
                payload['message']['form'] = int(key)
                found = True
                break
        if not found:
            print "Not a valid value, using default"
            payload["message"]["form"] = int(default_form_id)
    print "Encounters enabled?\n>",
    if raw_input() in truthy:
        payload["message"]["player_level"] = 30
        payload["message"]["height"] = 0.5694651007652283
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
        if payload["message"]["pokemon_id"] == 19:
            print "Count towards tiny Rattata medal?\n>",
            if raw_input() in truthy:
                payload["message"]["weight"] = 2.0
        if payload["message"]["pokemon_id"] == 129:
            print "Count towards big Magikarp medal?\n>",
            if raw_input() in truthy:
                payload["message"]["weight"] = 14.0
        print "Monster level?\n>",
        int_or_default("pokemon_level")
    print "What type of weather? (number only)(Default: None)\n" + \
          weather_formatted + "\n>",
    int_or_default("weather")
    print "Is this mon boosted by the weather? (y/n)\n>",
    if raw_input() in truthy:
        payload["message"]["boosted_weather"] = payload["message"]["weather"]
elif type == whtypes["3"]:
    gym_cache()
    print "Which team?(put in a number)\n" + teams_formatted + "\n>",
    get_and_validate_team()
elif type == whtypes["4"]:
    gym_cache()
    print "Which team?(put in a number)\n" + teams_formatted + "\n>",
    get_and_validate_team()
elif type == whtypes["5"]:
    gym_cache()
    print "Enter pokemon id for raid\n>",
    int_or_default("pokemon_id")
    print "Which team?(put in a number)\n" + teams_formatted + "\n>",
    get_and_validate_team()
    print "Moveset important?\n>",
    if raw_input() in truthy:
        print "Id of move 1\n>",
        int_or_default("move_1")
        print "Id of move 2\n>",
        int_or_default("move_2")
    print "What type of weather? (put in a number)\n" + \
          weather_formatted + "\n>",
    int_or_default("weather")
elif type == whtypes["6"]:
    print "What type of weather would you like to report? (Default: 0)\n" +\
          weather_formatted + '\n>',
    int_or_default("gameplay_weather")
    print "What type of severity status would you like? (Default: 0)\n" \
          + severity_formatted + '\n>',
    int_or_default("severity")
    print "Day or night? (Put in number, Default: 1)\n" + \
          day_or_night_formatted + '\n>',
    int_or_default("world_time")

if type in ["4", "5"]:
    print "What level of raid/egg? (1-5)\n>",
    level = check_int(raw_input(), payload["message"]["level"])
    if 6 > level > 0:
        payload["message"]["level"] = level
    else:
        print "Egg/Raid level invalid. Assuming level 5"

reset_timers_and_encounters()

while True:
    for i in range(3):
        resp = requests.post(url, json=payload, timeout=5)
        if resp.ok is True:
            print "Notification successful. Returned code {}".format(
                resp.status_code)
            break
        else:
            print "Discord response was {}".format(resp.content)
            raise requests.exceptions.RequestException(
                "Response received {}, webhook not accepted.".format(
                    resp.status_code))
            print "Attempting connection again"
    print "Send again?\n>",
    if raw_input() not in truthy:
        break
    if payload["type"] == "gym":
        print "Which team? (put in number)" + teams_formatted + "\n>",
        get_and_validate_team()
    reset_timers_and_encounters()

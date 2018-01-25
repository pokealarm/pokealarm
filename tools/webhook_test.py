import requests
import time
import sys
import json
import re
import os
import portalocker
import pickle

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

weather = {
    "0": "None",
    "1": "Clear",
    "2": "Rain",
    "3": "Partly Cloudy",
    "4": "Cloudy",
    "5": "Windy",
    "6": "Snow",
    "7": "Fog"
}

teams_formatted = re.sub('[{}",]', '', json.dumps(
    teams, indent=4, sort_keys=True))

weather_formatted = re.sub('[{}",]', '', json.dumps(
    weather, indent=4, sort_keys=True))

_cache = {}

_gym_info = {}


def get_image_url(image):
    return \
        "https://raw.githubusercontent.com/not4profit/images/master/" + image


_default_gym_info = {
    "name": "unknown",
    "description": "unknown",
    "url": get_image_url('icons/gym_0.png')
}


def set_init(webhook_type):
    payloadr = {}
    current_time = time.time()
    if webhook_type == whtypes["1"]:
        payloadr = {
            "type": "pokemon",
            "message": {
                "pokemon_id": 149,
                "pokemon_level": 30,
                "player_level": 30,
                "latitude": 37.7876146,
                "longitude": -122.390624,
                "encounter_id": current_time,
                "cp_multiplier": 0.7317000031471252,
                "form": None,
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
                "verified": False,
                "weather": 0,
                "boosted_weather": 0
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
                "gym_id": 0,
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
                "gym_id": 0,
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
                "gym_id": 0,
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
    return _gym_info.get(gym_id, _default_gym_info)


def gym_or_invalid(prm, prm2):
    questionable_input = raw_input()
    while get_gym_info(questionable_input)['name'] == "unknown":
        print "Not a valid gym. Please try again..\n>",
        questionable_input = raw_input()
    print "Gym found! {}".format(get_gym_info(questionable_input)['name'])
    payload["message"][prm] = questionable_input
    payload["message"][prm2] = get_gym_info(questionable_input)['name']


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
        _gym_info = data.get('gym_info', {})


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
            for key in _gym_info.keys():
                i += 1
                name = get_gym_info(key)['name']
                f.write("[{}] {} : {} \n".format(i, name, key))
            f.close()
        print "Find list of gyms in your \\tools\ folder (gyms.txt)"
        print "Enter gym id for raid (from file)\n>",
    else:
        print "Here is a list of gyms found in your cache:"
        i = 0
        for key in _gym_info.keys():
            i += 1
            name = get_gym_info(key)['name']
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
            "start": current_time + 20,
            "end": current_time + 20 + 60,
        })


def get_and_validate_team():
    team = teams.get(raw_input(), 5)
    if team == 5:
        print "Team invalid, defaulting to Uncontested"
        team = 0
    else:
        for team_id, team_name in teams.iteritems():
            if team_name == team:
                team = int(team_id)
    payload["message"]["team_id"] = team


webhooks_formatted = re.sub('[{}",]', '', json.dumps(
    whtypes, indent=4, sort_keys=True))
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
    if payload["message"]["pokemon_id"] == 201:
        print "Which form of Unown would you like? (default: A)\n>",
        form_character = raw_input()[0:1].upper()
        if form_character == '':
            print "Defaulting to A"
            payload["message"]["form"] = 1
        else:
            form = ord(form_character)
            # A-Z = 1-26, ! = 27, ? = 28
            if ord('A') <= form <= ord('Z'):
                form -= ord('A') - 1
            elif form == 33:
                # !
                form = 27
            elif form == 63:
                # ?
                form = 28
            else:
                print "Invalid form type. Defaulting to A"
                form = 1
            payload["message"]["form"] = form
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
        if payload["message"]["pokemon_id"] == 19:
            print "Count towards tiny Rattata medal?"
            if raw_input() in truthy:
                payload["message"]["weight"] = 2.0
        if payload["message"]["pokemon_id"] == 129:
            print "Count towards big Magikarp medal?"
            if raw_input() in truthy:
                payload["message"]["weight"] = 14.0
    print "What type of weather? (put in a number)\n" + \
          weather_formatted + "\n>",
    int_or_default("weather")
    print "Is this mon boosted by the weather? (y/n)\n",
    if raw_input() in truthy:
        payload["message"]["boosted_weather"] = payload["message"]["weather"]
elif type == whtypes["3"]:
    gym_cache()
    print "Which team?(put in a number)\n" + teams_formatted + "\n>",
    get_and_validate_team()
elif type == whtypes["4"]:
    gym_cache()
    print "What level of gym egg? (1-5)\n>",
    egglevel = check_int(raw_input(), payload["message"]["level"])
    if 6 > egglevel > 0:
        payload["message"]["level"] = egglevel
    else:
        print "Egg level invalid. Assuming level 5"
elif type == whtypes["5"]:
    gym_cache()
    print "Enter pokemon id for raid\n>",
    int_or_default("pokemon_id")
    print "Moveset important?\n>",
    if raw_input() in truthy:
        print "Id of move 1\n>",
        int_or_default("move_1")
        print "Id of move 2\n>",
        int_or_default("move_2")
    print "What type of weather? (put in a number)\n" + \
          weather_formatted + "\n>",
    int_or_default("weather")

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

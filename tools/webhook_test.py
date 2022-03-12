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
        print("The webhook_test.py file has moved from the PokeAlarm/tools"
              " folder!\nPlease put it back or re-download PokeAlarm.")
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
    "6": "weather",
    "7": "quest",
    "8": "invasion"
}

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
locales_file = glob(get_path('../locales/en.json'))[0]
data = json.loads(open(locales_file, 'rb+').read())
# Mon data
master_file = "https://raw.githubusercontent.com/WatWowMap/" \
    "Masterfile-Generator/master/master-latest-everything.json"
master_file = requests.get(master_file)
pokemon_data = master_file.json()["pokemon"]
# Invasion data
invasions_file = "https://raw.githubusercontent.com/cecpk/RocketMAD/" \
    "master/static/data/invasions.json"
invasions_data = requests.get(invasions_file).json()

teams_formatted = re.sub(
    r'[{}",]', '', json.dumps(data['teams'], indent=2, sort_keys=True))

weather_formatted = re.sub(
    r'[{}",]', '', json.dumps(data['weather'], indent=2, sort_keys=True))

severity_formatted = re.sub(
    r'[{}",]', '', json.dumps(data['severity'], indent=2, sort_keys=True))

day_or_night_formatted = re.sub(
    r'[{}",]', '', json.dumps(data['day_or_night'], indent=2, sort_keys=True))

quest_reward_types_formatted = re.sub(
    r'[{}",]', '', json.dumps(data['quest_reward_types'], indent=2,
                              sort_keys=True))

items_formatted = re.sub(
    r'[{}",]', '', json.dumps(data['items'], indent=2, sort_keys=True))

lure_types_formatted = re.sub(
    '[{}",]', '', json.dumps(data['lure_types'], indent=2, sort_keys=True))

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
                "weather": None
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
                "active_fort_modifier": 0,
                "lure_id": 501
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
                "form": 0,
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
    elif webhook_type == whtypes["7"]:
        payloadr = {
            "type": "quest",
            "message": {
                "pokestop_id": current_time,
                "pokestop_name": "Pokemon HQ",
                "pokestop_url": "http://placehold.it/500x500",
                "latitude": 37.7876146,
                "longitude": -122.390624,
                "timestamp": current_time,
                "quest_reward_type": "Pokemon",
                "quest_reward_type_raw": 7,
                "quest_target": 0,
                "quest_type": "Catch 10 Dragonites",
                "quest_type_raw": 0,
                "item_type": "Pokemon",
                "item_amount": 1,
                "item_id": 0,
                "pokemon_id": 123,
                "pokemon_form": 0,
                "quest_task": "Catch 10 Dragonites",
                "quest_condition": "[]",
                "quest_template": ""
            }
        }
    elif webhook_type == whtypes["8"]:
        payloadr = {
            "type": "invasion",
            "message": {
                "pokestop_id": current_time,
                "enabled": "True",
                "latitude": 37.7876146,
                "longitude": -122.390624,
                "active_fort_modifier": 0,
                "lure_expiration": 0,
                "incident_expiration": current_time,
                "incident_grunt_type": 30
            }
        }

    return payloadr


def check_int(questionable_input, default):
    if questionable_input.isdigit():
        return int(questionable_input.lstrip('-'))
    else:
        print(f"Invalid number, using default: {default}")
        return default


def int_or_default(input_parm):
    payload["message"][input_parm] = check_int(
        input(), payload["message"][input_parm])


def get_gym_info(gym_id):
    """ Gets the information about the gym. """
    return _gym_info.get(gym_id, 'unknown')


def gym_or_invalid(prm, prm2):
    questionable_input = input()
    while get_gym_info(questionable_input) == "unknown":
        print("Invalid gym. Please try again..", end='\n> ')
        questionable_input = input()
    print(f"Gym found! {get_gym_info(questionable_input)}")
    payload["message"][prm] = questionable_input
    payload["message"][prm2] = get_gym_info(questionable_input)


def cache_or_invalid():
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cache_input = input()
    if os.path.exists(os.path.join(path, "cache", f"{cache_input}.cache")):
        file = os.path.join(path, "cache", "{cache_input}.cache")
        print(f"Valid file: {file}")
    elif os.path.exists(os.path.join(path, "cache", "manager_0.cache")):
        file = os.path.join(path, "cache", "manager_0.cache")
        print(f"Invalid file, using default: {file}")
    else:
        print("No valid cache file found, terminating..")
        sys.exit(1)
    load_gym_cache(file)


def load_gym_cache(file):
    global _gym_info
    with portalocker.Lock(file, mode='rb') as f:
        gym_data = pickle.load(f, encoding='utf-8')
        _gym_info = gym_data.get('gym_name', {})


def list_cache():
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if not os.path.exists(os.path.join(path, "cache")):
        print("Cache folder does not exist! No cache file found")
        return False
    print("Here is a list of cache files found in cache:")
    for file in os.listdir(os.path.join(path, "cache")):
        if file.endswith('.cache'):
            print(file)
    return True


def list_gyms():
    path = os.path.dirname(os.path.abspath(__file__))
    if len(_gym_info) > 50:
        with portalocker.Lock(os.path.join(path, "gyms.txt"), mode='wb+') as f:
            gym_index = 0
            for key, name in _gym_info.items():
                gym_index += 1
                f.write(f"[{gym_index}] {name}: {key} \n".encode())
            f.close()
        print("Find list of gyms in your tools folder (gyms.txt)")
        print("Enter gym ID for raid (from file)", end='\n> ')
    else:
        print("Here is a list of gyms found in your cache:")
        gym_index = 0
        for key, name in _gym_info.items():
            gym_index += 1
            print(f"[{gym_index}] {name}: {key}".encode())
        print("Enter gym ID for raid (from above)", end='\n> ')


def gym_cache():
    print("Do you use file caching or does 'gym name' matter? (y/n)",
          end='\n> ')
    if input() in truthy:
        if not list_cache():
            return False
        print("Enter cache file name to verify the gym"
              " (default: manager_0)", end='\n> ')
        cache_or_invalid()
        list_gyms()
        gym_or_invalid('gym_id', 'gym_name')


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
    elif payload["type"] == "quest":
        payload["message"].update({
            "stop_id": current_time,
            'timestamp': current_time
        })
    elif payload["type"] == "invasion":
        payload["message"].update({
            "last_modified_time": current_time,
            "incident_expiration": current_time + 60,
        })


def get_and_validate_team():
    team = data['teams'].get(input(), 5)
    if team == 5:
        print("Invalid team, using default: 0")
        team = 0
    else:
        for team_id, team_name in data['teams'].items():
            if team_name == team:
                team = int(team_id)
                break
    payload["message"]["team_id"] = team


def monster_form(webhook_field, monster_id):
    monster_id_formatted = f"{monster_id:03d}"

    raw_form_names = get_raw_form_names()
    english_form_names = {}
    for id_ in raw_form_names:
        english_form_names[id_] = {}
        for form_id_ in raw_form_names[id_]:
            english_form_names[id_][form_id_] = (data[
                'form_names'].get(raw_form_names[id_][form_id_]) or
                raw_form_names[id_][form_id_])

    sorted_forms = []
    default_form_id = 0
    monster_forms_dict = english_form_names[monster_id]
    if len(monster_forms_dict) > 1:
        monster_forms_dict.pop(0)
        sorted_forms = sorted(monster_forms_dict)
        default_form_id = next(iter(sorted_forms))
        forms_formatted = ', '.join(monster_forms_dict[x]
                                    for x in sorted_forms)
    else:
        sorted_forms = sorted(monster_forms_dict)
        default_form_id = next(iter(sorted_forms))
        forms_formatted = ', '.join(monster_forms_dict[x]
                                    for x in sorted_forms)

    print(f"Which form of {data['pokemon'][monster_id_formatted]}"
          " would you like? (default:"
          f" {monster_forms_dict[default_form_id]})")
    print(forms_formatted, end='\n> ')
    form_character = input().lower()
    found = False
    for key, x in monster_forms_dict.items():
        if x.lower() == form_character:
            payload['message'][webhook_field] = int(key)
            found = True
            break
    if not found:
        print("Invalid value, using default")
        payload["message"][webhook_field] = int(default_form_id)


def get_raw_form_names():
    if not hasattr(get_raw_form_names, 'info'):
        get_raw_form_names.info = {}
        for id_ in pokemon_data:
            get_raw_form_names.info[int(id_)] = {}
            get_raw_form_names.info[int(id_)][0] = "Normal"
            for form_id_ in pokemon_data[id_]["forms"]:
                if form_id_ != "0":
                    get_raw_form_names.info[int(id_)][
                        int(form_id_)] = pokemon_data[id_]["forms"
                                                           ][form_id_]["name"]

    return get_raw_form_names.info


def get_invasion_list_str():
    invasions_str = ""
    for id_ in invasions_data:
        invasions_str += f"{id_}: {invasions_data[id_]['type']}\n"

    return invasions_str


def stop_info(id_field_name, url_field_name, name_field_name):
    print("Pokestop ID", end='\n> ')
    payload['message'][id_field_name] = input()
    print("What is the pokestop URL you'd like to show as the image?",
          end='\n> ')
    payload['message'][url_field_name] = input()
    print("Pokestop name", end='\n> ')
    payload['message'][name_field_name] = input()


webhooks_formatted = re.sub('[{}",]', '', json.dumps(
    whtypes, indent=2, sort_keys=True))
print("What kind of webhook would you like to send? (1-8)")
print(webhooks_formatted, end='\n> ')

type = whtypes.get(input(), 0)
while type == 0:
    print("Invalid webhook type. Please try again..", end='\n> ')
    type = whtypes.get(input(), 0)

payload = set_init(type)
default_url = "http://127.0.0.1:4000"

print("What is the URL of where you would like to send the webhook?"
      f" (default: {default_url})", end='\n> ')
url = input()
if url == '' or url.isspace():
    url = default_url
    print(f"Using default: {url}")

print("Does location matter or do you use geofences? (y/n)", end='\n> ')
if input() in truthy:
    regex_coordinates = re.compile(
        r"[-+]?[0-9]*\.?[0-9]*" + r"[ \t]*,[ \t]*" + r"[-+]?[0-9]*\.?[0-9]*")
    print("Enter latitude,longitude (ex: 37.7876146,-122.390624)", end='\n> ')
    coordinates = input()
    lat = payload["message"]["latitude"]
    lng = payload["message"]["longitude"]
    if not regex_coordinates.match(coordinates):
        print(f"Invalid coordinates, using default: {lat},{lng}")
    else:
        lat, lng = map(float, coordinates.split(","))
    payload["message"]["latitude"] = lat
    payload["message"]["longitude"] = lng

if type == whtypes["1"]:
    print("Pokemon ID (default: 149)", end='\n> ')
    int_or_default('pokemon_id')
    print("Gender (1-3) (default: 3)", end='\n> ')
    int_or_default('gender')
    monster_form('form', payload['message']['pokemon_id'])
    print("Encounter enabled? (y/n)", end='\n> ')
    if input() in truthy:
        payload["message"]["player_level"] = 30
        payload["message"]["height"] = 0.5694651007652283
        print("CP", end='\n> ')
        int_or_default('cp')
        print("Attack IV", end='\n> ')
        int_or_default('individual_attack')
        print("Defense IV", end='\n> ')
        int_or_default('individual_defense')
        print("Stamina IV", end='\n> ')
        int_or_default('individual_stamina')
        print("ID of move 1", end='\n> ')
        int_or_default('move_1')
        print("ID of move 2", end='\n> ')
        int_or_default('move_2')
        if payload["message"]["pokemon_id"] == 19:
            print("Count towards tiny Rattata medal? (y/n)", end='\n> ')
            if input() in truthy:
                payload["message"]["weight"] = 2.0
        if payload["message"]["pokemon_id"] == 129:
            print("Count towards big Magikarp medal? (y/n)", end='\n> ')
            if input() in truthy:
                payload["message"]["weight"] = 14.0
        print("Pokemon level", end='\n> ')
        int_or_default('pokemon_level')
    print("Weather type (default: 0)")
    print(weather_formatted, end='\n> ')
    int_or_default('weather')
elif type == whtypes["2"]:
    stop_info('pokestop_id', 'url', 'name')
    print("Lure type (default: 501)")
    print(lure_types_formatted, end='\n> ')
    int_or_default('lure_id')
elif type == whtypes["3"]:
    gym_cache()
    print("Team (default: 0)")
    print(teams_formatted, end='\n> ')
    get_and_validate_team()
elif type == whtypes["4"]:
    gym_cache()
    print("Team (default: 0)")
    print(teams_formatted, end='\n> ')
    get_and_validate_team()
elif type == whtypes["5"]:
    gym_cache()
    print("Pokemon ID (default: 150)", end='\n> ')
    int_or_default('pokemon_id')
    monster_form('form', payload['message']['pokemon_id'])
    print("Team (default: 0)")
    print(teams_formatted, end='\n> ')
    get_and_validate_team()
    print("Moveset important? (y/n)", end='\n> ')
    if input() in truthy:
        print("ID of move 1", end='\n> ')
        int_or_default('move_1')
        print("ID of move 2", end='\n> ')
        int_or_default('move_2')
    print("Weather type (default: 0)")
    print(weather_formatted, end='\n> ')
    int_or_default('weather')
elif type == whtypes["6"]:
    print("What type of weather would you like to report? (default: 0)")
    print(weather_formatted, end='\n> ')
    int_or_default('gameplay_weather')
    print("What type of severity status would you like? (default: 0)")
    print(severity_formatted, end='\n> ')
    int_or_default('severity')
    print("Day or night (default: 1)")
    print(day_or_night_formatted, end='\n> ')
    int_or_default('world_time')
elif type == whtypes["7"]:
    print("What is the user required to do to get the reward?", end='\n> ')
    payload['message']['quest_task'] = input()
    print("What quest reward type is it? (default: 7)")
    print(quest_reward_types_formatted, end='\n> ')
    int_or_default('quest_reward_type_raw')
    reward_type = payload['message']['quest_reward_type_raw']
    if reward_type != 7:
        print("How many of that reward type?", end='\n> ')
        int_or_default('item_amount')
    if reward_type == 7:
        print("Pokemon ID (default: 123)", end='\n> ')
        int_or_default('pokemon_id')
        monster_form('pokemon_form', payload['message']['pokemon_id'])
    if reward_type == 2:
        print("Item (default: 0)")
        print(items_formatted, end='\n> ')
        int_or_default('item_id')
elif type == whtypes["8"]:
    print("Grunt ID (default: 30)")
    print(get_invasion_list_str(), end='\n> ')
    int_or_default('incident_grunt_type')

if type in ["4", "5"]:
    print("Raid/egg level", end='\n> ')
    payload["message"]["level"] = check_int(
        input(), payload["message"]["level"])

reset_timers_and_encounters()

while True:
    try:
        for i in range(3):
            resp = requests.post(url, json=payload, timeout=5)
            if resp.ok is True:
                print("Notification successful."
                      + f" Returned code {resp.status_code}")
                break
            else:
                print(f"Discord response was {resp.content}")
                raise requests.exceptions.RequestException(
                    f"Response received {resp.status_code}, "
                    + "webhook not accepted.")
    except requests.exceptions.ConnectionError:
        print(f"Cannot send webhook to {url}. Check the webhook URL"
              " or if your PA server is running.")
    print("Send again? (y/n)", end='\n> ')
    if input() not in truthy:
        break
    if payload["type"] == "gym":
        print("Team (default: 0)")
        print(teams_formatted, end='\n> ')
        get_and_validate_team()
    reset_timers_and_encounters()


# TO USE:
#   Comment and uncomment the particular version of "payload" based off which type of webhook you wish to send
#   put your PA webhook url into the "url" variable

import requests
import logging
import time

logging.basicConfig(format='%(asctime)s [%(processName)15.15s][%(name)10.10s][%(levelname)8.8s] %(message)s',
                    level=logging.INFO)

log = logging.getLogger('Server')

url = 'http://127.0.0.1'

payload = {
    "type": "pokemon",
    "message": {
        "encounter_id": "0",
        "pokemon_id": 149,
        "pokemon_level": 30,
        "player_level": 30,
        "latitude": 33.980823,
        "longitude":  -81.052988,
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
        "gender": 3
    }
}

# payload = {
#     "type": "pokestop",
#     "message": {
#         "pokestop_id": 0,
#         "enabled": "True",
#         "latitude": 62.790967,
#         "longitude":  76.927920,
#         "active_fort_modifier": 0
#     }
# }

# payload = {
#     "type": "gym",
#     "message": {
#         "raid_active_until": 0,
#         "gym_id": 0,
#         "team_id": 3,
#         "guard_pokemon_id": 0,
#         "gym_points": 100,
#         "slots_available": 0,
#         "guard_pokemon_id": 99,
#         "lowest_pokemon_motivation": 0.8795773983001709,
#         "total_cp": 11099,
#         "enabled": "True",
#         "latitude": 62.790967,
#         "longitude":  76.927920
#     }
# }

# payload = {
#     "type": "raid",
#     "message": {
#         "gym_id": "gym_id",
#         "level": 5,
#         "latitude": 12.345678,
#         "longitude": 12.345678
#     }
# }

# payload = {
#     "type": "raid",
#     "message": {
#         "gym_id": "gym_id",
#         "pokemon_id": 150,
#         "cp": 12345,
#         "move_1": 123,
#         "move_2": 123,
#         "level": 5,
#         "latitude": 12.345678,
#         "longitude": 12.345678
#     }
# }

time = time.time()
if payload["type"] == "pokemon":
    payload["message"].update({
        "disappear_time": time + 10,
        "last_modified_time": time,
        "time_until_hidden_ms": 10000
   })
elif payload["type"] == "pokestop":
    payload["message"].update({
        "last_modified_time": time,
        "lure_expiration": time + 60,
    })
elif payload["type"] == "gym":
    payload["message"].update({
        "last_modified": time,
        "occupied_since": time - 9000
    })
elif payload["type"] == "raid":
    payload["message"].update({
        "start": time + 20,
        "end": time + 20 + 60,
    })

for i in range(3):
    resp = requests.post(url, json=payload, timeout=5)
    if resp.ok is True:
        log.info("Notification successful (returned {})".format(resp.status_code))
        break
    else:
        log.info("Discord response was {}".format(resp.content))
        raise requests.exceptions.RequestException(
            "Response received {}, webhook not accepted.".format(resp.status_code))
        log.info("Attempting connection again")
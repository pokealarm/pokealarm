import requests
import logging

logging.basicConfig(format='%(asctime)s [%(processName)15.15s][%(name)10.10s][%(levelname)8.8s] %(message)s',
                    level=logging.INFO)

log = logging.getLogger('Server')

url = 'http://127.0.0.1'
payload = {
    "type": "pokemon",
    "message": {
        "encounter_id": "0",
        "pokemon_id": 1,
        "pokemon_level": 30,
        "player_level": 30,
        "latitude": 33.980823,
        "longitude":  -81.052988,
        "disappear_time": 1506897031,
        "last_modified_time": 1475033386661,
        "time_until_hidden_ms": 5000,
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
#         "last_modified_time": 1572241600,
#         "lure_expiration": 1572241600,
#         "active_fort_modifier": 0
#     }
# }

# payload = {
#     "type": "gyms",
#     "message": {
# 		"raid_active_until": 0,
# 		"gym_id": 0,
# 		"team_id": 0,
# 		"guard_pokemon_id": 0,
# 		"gym_points": 100,
# 		"slots_available": 0,
# 		"guard_pokemon_id": 99,
# 		"lowest_pokemon_motivation": 0.8795773983001709,
# 		"total_cp": 11099,
#                 "occupied_since": 1506886787,
# 		"enabled": "True",
# 		"latitude": 62.790967,
# 		"longitude":  76.927920,
# 		"last_modified": 1572241600
#     }
# }

# payload = {
#     "type": "raid",
#     "message": {
#         "gym_id": "gym_id",
#         "start": 1499244052,
#         "end": 1499246052 ,
#         "level": 5,
#         "latitude": 12.345678,
#         "longitude": 12.345678
#     }
# }

# payload = {
#     "type": "raid",
#     "message": {
#         "gym_id": "gym_id",
#         "pokemon_id": 200,
#         "cp": 12345,
#         "move_1": 123,
#         "move_2": 123,
#         "start": 1499244052,
#         "end": 1499246052 ,
#         "level": 5,
#         "latitude": 12.345678,
#         "longitude": 12.345678
#     }
# }

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
# Webhook Standard

## Overview

* [Pokemon](#pokemon)
* [Pokestops](#pokestops)
* [Gyms](#gyms)
  * [Gym-details Example](#gym-details-example)
* [Egg example](#egg-example)
* [Raid example](#raid-example)

## Pokemon

Pokemon standard now includes moveset and IVs as of commit [oc1b4](https://github.com/RocketMap/PokeAlarm/commit/0c1b4cce80e0ceb3cc6dbb2d802204af4dd3ce60).

#### Example:

```json
{
    "type": "pokemon",
    "message": {
        "encounter_id": "0",
        "spawnpoint_id": "0",
        "pokemon_id": 201,
        "pokemon_level": 30,
        "player_level": 31,
        "latitude": 37.7876146,
        "longitude": -122.390624,
        "disappear_time": 1506897031,
        "last_modified_time": 1475033386661,
        "time_until_hidden_ms": 5000,
        "seconds_until_despawn": 1754,
        "spawn_start": 2153,
        "spawn_end": 3264,
        "verified": false,
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
```

## Pokestops

#### Example:

```json
{
    "type": "pokestop",
    "message": {
        "pokestop_id": 0,
        "enabled": "True",
        "latitude": 37.7876146,
        "longitude": -122.390624,
        "last_modified_time": 1572241600,
        "lure_expiration": 1572241600,
        "active_fort_modifier": 0
    }
}
```

## Gyms

#### Example:

```json
{
    "type": "gyms",
    "message": {
				"raid_active_until": 0,
				"gym_id": 0,
				"team_id": 0,
				"guard_pokemon_id": 0,
				"slots_available": 0,
				"guard_pokemon_id": 99,
				"lowest_pokemon_motivation": 0.8795773983001709,
				"total_cp": 11099,
				"occupied_since": 1506886787,
				"enabled": "True",
				"latitude": 37.7876146,
				"longitude": -122.390624,
				"last_modified": 1572241600
    }
}
```

#### Gym-details example:

```json
{
    "type": "gym_details",
    "message": {
        "id": "OWNmOTFmMmM0YTY3NGQwYjg0Y2I1N2JlZjU4OWRkMTYuMTY=",
        "url": "http://lh3.ggpht.com/yBqXtFfq3nOlZmLc7DbgSIcXcyfvsWfY3VQs_gBziPwjUx7xOfgvucz6uxP_Ri-ianoWFt5mgJ7_zpsa7VNK",
        "name": "Graduate School of Public Health Sculpture",
        "description": "Sculpture on the exterior of the Graduate School of Public Health building.",
        "team": 1,
        "latitude": 37.7876146,
        "longitude": -122.390624,
        "pokemon": [{
            "num_upgrades": 0,
            "move_1": 234,
            "move_2": 99,
            "additional_cp_multiplier": 0,
            "iv_defense": 11,
            "weight": 14.138585090637207,
            "pokemon_id": 63,
            "stamina_max": 46,
            "cp_multiplier": 0.39956727623939514,
            "height": 0.7160492539405823,
            "stamina": 46,
            "pokemon_uid": 9278614152997308833,
            "deployment_time": 1506894280,
            "iv_attack": 12,
            "trainer_name": "SportyGator",
            "trainer_level": 18,
            "cp": 138,
            "iv_stamina": 8,
            "cp_decayed": 125
        }, {
            "num_upgrades": 0,
            "move_1": 234,
            "move_2": 87,
            "additional_cp_multiplier": 0,
            "iv_defense": 12,
            "weight": 3.51259708404541,
            "pokemon_id": 36,
            "stamina_max": 250,
            "cp_multiplier": 0.6121572852134705,
            "height": 1.4966495037078857,
            "stamina": 250,
            "pokemon_uid": 6103380929145641793,
            "deployment_time": 1506894733,
            "iv_attack": 5,
            "trainer_name": "Meckelangelo",
            "trainer_level": 22,
            "cp": 1353,
            "iv_stamina": 15,
            "cp_decayed": 1024
        }, {
            "num_upgrades": 9,
            "move_1": 224,
            "move_2": 32,
            "additional_cp_multiplier": 0.06381925195455551,
            "iv_defense": 13,
            "weight": 60.0,
            "pokemon_id": 31,
            "stamina_max": 252,
            "cp_multiplier": 0.5974000096321106,
            "height": 1.0611374378204346,
            "stamina": 252,
            "pokemon_uid": 3580711458547635980,
            "deployment_time": 1506894763,
            "iv_attack": 10,
            "trainer_name": "Plaidflamingo",
            "trainer_level": 23,
            "cp": 1670,
            "iv_stamina": 11,
            "cp_decayed": 1435
        }]
    }
}
```

## Egg example

Take note that the type for egg is `raid` because it is collected from the same
webhook event from RocketMap as raids are.

```json
{
    "type": "raid",
    "message": {
        "gym_id": "gym_id",
        "start": 1499244052,
        "end": 1499246052,
        "level": 5,
        "latitude": 37.7876146,
        "longitude": -122.390624
    }
}
```

## Raid example

```json
{
    "type": "raid",
    "message": {
        "gym_id": "gym_id",
        "pokemon_id": 200,
        "cp": 12345,
        "move_1": 123,
        "move_2": 123,
        "start": 1499244052,
        "end": 1499246052,
        "level": 5,
        "latitude": 37.7876146,
        "longitude": -122.390624
    }
}
```

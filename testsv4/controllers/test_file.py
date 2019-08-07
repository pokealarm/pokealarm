# Standard Library Imports
import asyncio
import calendar
import unittest
from datetime import datetime, timedelta
# 3rd Party Imports
# Local Imports
from pokealarmv4.controllers import EventFileController
from pokealarmv4.events import Monster


def generic_monster(values):
    """ Generate a generic monster, overriding with an specific values. """
    settings = {
        "encounter_id": str(datetime.utcnow()),
        "disappear_time": calendar.timegm(
            (datetime.utcnow() + timedelta(minutes=45)).timetuple()),
        "spawnpoint_id": "0",
        "pokemon_id": 1,
        "pokemon_level": 1,
        "player_level": 40,
        "latitude": 37.7876146,
        "longitude": -122.390624,
        "last_modified_time": 1475033386661,
        "time_until_hidden_ms": 5000,
        "seconds_until_despawn": 1754,
        "spawn_start": 2153,
        "spawn_end": 3264,
        "verified": False,
        "cp_multiplier": 0.7317000031471252,
        "form": None,
        "cp": None,
        "individual_attack": None,
        "individual_defense": None,
        "individual_stamina": None,
        "move_1": None,
        "move_2": None,
        "height": None,
        "weight": None,
        "gender": None
    }
    settings.update(values)
    return Monster(settings)


def async_test(test):
    def wrapper(*args, **kwargs):
        future = test(*args, **kwargs)
        asyncio.get_event_loop().run_until_complete(future)
    return wrapper


class TestFileController(unittest.TestCase):

    @async_test
    async def test_mon_update(self):
        id = str(datetime.utcnow())
        # Create a test event and update in controller
        mon = generic_monster({"encounter_id": id, "pokemon_id": 2})
        fc = EventFileController("test_event_file.bin")
        old_mon = await fc.update(mon)
        self.assertEqual(old_mon, None)
        self.assertEqual(mon.monster_id, 2)

        # Create updated test event and update in controller
        new_mon = generic_monster({"encounter_id": id, "pokemon_id": 3})
        old_mon = await fc.update(new_mon)
        self.assertEqual(old_mon, mon)
        self.assertEqual(new_mon.monster_id, 3)

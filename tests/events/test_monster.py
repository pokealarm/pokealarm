# -*- coding: utf-8 -*-

# Standard Library Imports
import calendar
import unittest
from datetime import datetime, timedelta
# 3rd Party Imports
# Local Imports
# from tests import context
from prototype.events import Monster


def generic_monster(values):
    """ Generate a generic monster, overriding with an specific values. """
    settings = {
        "encounter_id": str(datetime.utcnow()),
        "disappear_time":  calendar.timegm(
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


class TestMonsterEvent(unittest.TestCase):

    def test_enc_id(self):
        mon = generic_monster({'encounter_id': 1})
        self.assertTrue(isinstance(mon.enc_id, str))
        self.assertTrue(mon.enc_id == "1")

    def test_monster_id(self):
        mon = generic_monster({'pokemon_id': 1})
        self.assertTrue(isinstance(mon.monster_id, int))
        self.assertTrue(mon.monster_id == 1)

    def test_disappear_time(self):
        mon = generic_monster({})
        self.assertTrue(isinstance(mon.disappear_time, datetime))

    def test_time_left(self):
        future = datetime.utcnow() + timedelta(seconds=30)
        mon = generic_monster(
            {'disappear_time': calendar.timegm(future.timetuple())})
        self.assertTrue(isinstance(mon.time_left, float))
        self.assertTrue(0 == int(mon.time_left - 30))

    def test_lat(self):
        mon = generic_monster({'latitude': 0})
        self.assertTrue(isinstance(mon.lat, float))
        self.assertTrue(mon.lat == 0.0)

    def test_lng(self):
        mon = generic_monster({'longitude': 0})
        self.assertTrue(isinstance(mon.lng, float))
        self.assertTrue(mon.lng == 0.0)

    def test_spawn_start(self):
        mon = generic_monster({'spawn_start': 5})
        self.assertTrue(isinstance(mon.spawn_start, int))
        self.assertTrue(mon.spawn_start == 5)

    def test_spawn_end(self):
        mon = generic_monster({'spawn_end': 5})
        self.assertTrue(isinstance(mon.spawn_end, int))
        self.assertTrue(mon.spawn_end == 5)

    def test_spawn_verified(self):
        mon = generic_monster({'verified': True})
        self.assertTrue(isinstance(mon.spawn_verified, bool))
        self.assertTrue(mon.spawn_verified)

    def test_mon_lvl(self):
        mon = generic_monster({'pokemon_level': 35})
        self.assertTrue(isinstance(mon.mon_lvl, int))
        self.assertTrue(mon.mon_lvl == 35)

    def test_cp(self):
        mon = generic_monster({'cp': 1000})
        self.assertTrue(isinstance(mon.cp, int))
        self.assertTrue(mon.cp == 1000)

    def test_atk_iv(self):
        mon = generic_monster({'individual_attack': 15})
        self.assertTrue(isinstance(mon.atk_iv, int))
        self.assertTrue(mon.atk_iv == 15)

    def test_def_iv(self):
        mon = generic_monster({'individual_defense': 15})
        self.assertTrue(isinstance(mon.def_iv, int))
        self.assertTrue(mon.def_iv == 15)

    def test_sta_iv(self):
        mon = generic_monster({'individual_stamina': 15})
        self.assertTrue(isinstance(mon.sta_iv, int))
        self.assertTrue(mon.sta_iv == 15)

    def test_iv(self):
        mon = generic_monster({
            'individual_attack': 15,
            'individual_defense': 15,
            'individual_stamina': 15
        })
        self.assertTrue(isinstance(mon.iv, float))
        self.assertTrue(mon.iv == 100.0)

    def test_quick_id(self):
        mon = generic_monster({'move_1': 17})
        self.assertTrue(isinstance(mon.quick_id, int))
        self.assertTrue(mon.quick_id == 17)

    def test_charge_id(self):
        mon = generic_monster({'move_2': 25})
        self.assertTrue(isinstance(mon.charge_id, int))
        self.assertTrue(mon.charge_id == 25)

    def test_atk_grade(self):
        mon = generic_monster({'atk_grade': "A"})
        self.assertTrue(isinstance(mon.atk_grade, str))
        self.assertTrue(mon.atk_grade == "A")

    def test_def_grade(self):
        mon = generic_monster({'def_grade': "D"})
        self.assertTrue(isinstance(mon.def_grade, str))
        self.assertTrue(mon.def_grade == "D")

    def test_gender_id(self):
        mon = generic_monster({'gender': 1})
        self.assertTrue(isinstance(mon.gender_id, int))
        self.assertTrue(mon.gender_id == 1)

    def test_height(self):
        mon = generic_monster({'height': 75.0})
        self.assertTrue(isinstance(mon.height, float))
        self.assertTrue(mon.height == 75.0)

    def test_weight(self):
        mon = generic_monster({'weight': 100.0})
        self.assertTrue(isinstance(mon.weight, float))
        self.assertTrue(mon.weight == 100.0)

    @unittest.skip("Not yet implemented")
    def test_size_id(self):
        self.fail("")

    def test_form_id(self):
        mon = generic_monster({'form': 12})
        self.assertTrue(isinstance(mon.form_id, int))
        self.assertTrue(mon.form_id == 12)

    def test_costume_id(self):
        mon = generic_monster({'costume': 3})
        self.assertTrue(isinstance(mon.costume_id, int))
        self.assertTrue(mon.costume_id == 3)

    def test_rarity(self):
        mon = generic_monster({'rarity': 5})
        self.assertTrue(isinstance(mon.rarity_id, int))
        self.assertTrue(mon.rarity_id == 5)

    def test_weather_id(self):
        mon = generic_monster({'weather': 5})
        self.assertTrue(isinstance(mon.weather_id, int))
        self.assertTrue(mon.weather_id == 5)

    def test_boosted_weather_id(self):
        mon = generic_monster({'boosted_weather': 3})
        self.assertTrue(isinstance(mon.boosted_weather_id, int))
        self.assertTrue(mon.boosted_weather_id == 3)

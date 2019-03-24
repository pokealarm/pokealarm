# -*- coding: utf-8 -*-

# Standard Library Imports
import calendar
from datetime import datetime, timedelta
import unittest
# 3rd Party Imports
# Local Imports
from pokealarmv4.events import Raid


def generic_raid(values):
    """ Generate a generic gym, overriding with an specific values. """
    settings = {
        "gym_id": "OWNmOTFmMmM0YTY3NGQwYjg0Y2I1N2JlZjU4OWRkMTYuMTY=",
        "url": None,
        "name": None,
        "description": None,
        "pokemon_id": 150,
        "cp": 12345,
        "move_1": 123,
        "move_2": 123,
        "start": 1499244052,
        "end": 1499246052,
        "level": 5,
        "latitude": 37.7876146,
        "longitude": -122.390624,
        "sponsor": None,
        "park": None
    }
    settings.update(values)
    return Raid(settings)


class TestRaidEvent(unittest.TestCase):

    def test_gym_id(self):
        raid = generic_raid({'gym_id': 1})
        self.assertTrue(isinstance(raid.gym_id, str))
        self.assertTrue(raid.gym_id == "1")

    def test_id(self):
        raid = generic_raid({'gym_id': 12345})
        self.assertTrue(isinstance(raid.id, int))
        self.assertTrue(raid.id == hash("12345"))

    def test_lat(self):
        raid = generic_raid({'latitude': 0})
        self.assertTrue(isinstance(raid.lat, float))
        self.assertTrue(raid.lat == 0.0)

    def test_lng(self):
        raid = generic_raid({'longitude': 0})
        self.assertTrue(isinstance(raid.lng, float))
        self.assertTrue(raid.lng == 0.0)

    def test_gym_name(self):
        raid = generic_raid({'name': "test123"})
        self.assertTrue(isinstance(raid.gym_name, str))
        self.assertTrue(raid.gym_name == "test123")

    def test_gym_description(self):
        raid = generic_raid({'description': "test123"})
        self.assertTrue(isinstance(raid.gym_description, str))
        self.assertTrue(raid.gym_description == "test123")

    def test_gym_image(self):
        raid = generic_raid({'url': "https://someimage.url"})
        self.assertTrue(isinstance(raid.gym_image, str))
        self.assertTrue(raid.gym_image == "https://someimage.url")

    def test_team_id(self):
        raid = generic_raid({'team_id': 1})
        self.assertTrue(isinstance(raid.team_id, int))
        self.assertTrue(raid.team_id == 1)

    def test_sponsor_id(self):
        raid = generic_raid({'sponsor': "3"})
        self.assertTrue(isinstance(raid.sponsor_id, int))
        self.assertTrue(raid.sponsor_id == 3)

    def test_park(self):
        raid = generic_raid({'park': "park_name"})
        self.assertTrue(isinstance(raid.park, str))
        self.assertTrue(raid.park == "park_name")

    def test_hatch_time(self):
        raid = generic_raid({})
        self.assertTrue(isinstance(raid.raid_end, datetime))

    def test_time_left(self):
        future = datetime.utcnow() + timedelta(seconds=30)
        raid = generic_raid(
            {'end': calendar.timegm(future.timetuple())})
        self.assertTrue(isinstance(raid.time_left, float))
        self.assertTrue(0 == int(raid.time_left - 30))

    def test_raid_lvl(self):
        raid = generic_raid({'level': "5"})
        self.assertTrue(isinstance(raid.raid_lvl, int))
        self.assertTrue(raid.raid_lvl == 5)

    def test_monster_id(self):
        raid = generic_raid({'pokemon_id': "20"})
        self.assertTrue(isinstance(raid.monster_id, int))
        self.assertTrue(raid.monster_id == 20)

    def test_cp(self):
        raid = generic_raid({'cp': "100"})
        self.assertTrue(isinstance(raid.cp, int))
        self.assertTrue(raid.cp == 100)

    def test_form_id(self):
        raid = generic_raid({'form': "5"})
        self.assertTrue(isinstance(raid.form_id, int))
        self.assertTrue(raid.form_id == 5)

    def test_costume_id(self):
        raid = generic_raid({'costume': "3"})
        self.assertTrue(isinstance(raid.costume_id, int))
        self.assertTrue(raid.costume_id == 3)

    def test_quick_id(self):
        raid = generic_raid({'move_1': "15"})
        self.assertTrue(isinstance(raid.quick_id, int))
        self.assertTrue(raid.quick_id == 15)

    def test_charge_id(self):
        raid = generic_raid({'move_2': "37"})
        self.assertTrue(isinstance(raid.charge_id, int))
        self.assertTrue(raid.charge_id == 37)

    def test_weather_id(self):
        raid = generic_raid({'weather': "7"})
        self.assertTrue(isinstance(raid.weather_id, int))
        self.assertTrue(raid.weather_id == 7)

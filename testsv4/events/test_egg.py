# Standard Library Imports
import calendar
from datetime import datetime, timedelta
import unittest
# 3rd Party Imports
# Local Imports
from pokealarmv4.events import Egg


def generic_egg(values):
    """ Generate a generic egg, overriding with an specific values. """
    settings = {
        "gym_id": "OWNmOTFmMmM0YTY3NGQwYjg0Y2I1N2JlZjU4OWRkMTYuMTY=",
        "url": None,
        "name": None,
        "description": None,
        "start": 1499244052,
        "end": 1499246052,
        "level": 5,
        "latitude": 37.7876146,
        "longitude": -122.390624,
        "weather": None,
        "sponsor": None,
        "park": None
    }
    settings.update(values)
    return Egg(settings)


class TestEggEvent(unittest.TestCase):

    def test_lat(self):
        egg = generic_egg({'latitude': 0})
        self.assertTrue(isinstance(egg.lat, float))
        self.assertTrue(egg.lat == 0.0)

    def test_lng(self):
        egg = generic_egg({'longitude': 0})
        self.assertTrue(isinstance(egg.lng, float))
        self.assertTrue(egg.lng == 0.0)

    def test_weather_id(self):
        egg = generic_egg({'weather': 0})
        self.assertTrue(isinstance(egg.weather_id, int))
        self.assertTrue(egg.weather_id == 0)

    def test_gym_id(self):
        egg = generic_egg({'gym_id': 1})
        self.assertTrue(isinstance(egg.gym_id, str))
        self.assertTrue(egg.gym_id == "1")

    def test_hatch_time(self):
        egg = generic_egg({})
        self.assertTrue(isinstance(egg.hatch_time, datetime))

    def test_time_left(self):
        future = datetime.utcnow() + timedelta(seconds=30)
        egg = generic_egg({'start': calendar.timegm(future.timetuple())})
        self.assertTrue(isinstance(egg.time_left, float))
        self.assertTrue(0 == int(egg.time_left - 30))

    def test_egg_lvl(self):
        egg = generic_egg({'level': "3"})
        self.assertTrue(isinstance(egg.egg_lvl, int))
        self.assertTrue(egg.egg_lvl == 3)

    def test_gym_name(self):
        egg = generic_egg({'name': "test123"})
        self.assertTrue(isinstance(egg.gym_name, str))
        self.assertTrue(egg.gym_name == "test123")

    def test_gym_description(self):
        egg = generic_egg({'description': "test123"})
        self.assertTrue(isinstance(egg.gym_description, str))
        self.assertTrue(egg.gym_description == "test123")

    def test_gym_image(self):
        egg = generic_egg({'url': "https://someimage.url"})
        self.assertTrue(isinstance(egg.gym_image, str))
        self.assertTrue(egg.gym_image == "https://someimage.url")

    def test_team_id(self):
        egg = generic_egg({'team_id': "3"})
        self.assertTrue(isinstance(egg.team_id, int))
        self.assertTrue(egg.team_id == 3)

    def test_sponsor_id(self):
        egg = generic_egg({'sponsor': "3"})
        self.assertTrue(isinstance(egg.sponsor_id, int))
        self.assertTrue(egg.sponsor_id == 3)

    def test_park_name(self):
        egg = generic_egg({'park': "park_name"})
        self.assertTrue(isinstance(egg.park_name, str))
        self.assertTrue(egg.park_name == "park_name")

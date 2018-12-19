# -*- coding: utf-8 -*-

# Standard Library Imports
import unittest
# 3rd Party Imports
# Local Imports
from pokealarmv4.events import Gym


def generic_gym(values):
    """ Generate a generic gym, overriding with an specific values. """
    settings = {
        "id": "OWNmOTFmMmM0YTY3NGQwYjg0Y2I1N2JlZjU4OWRkMTYuMTY=",
        "url": None,
        "name": None,
        "description": None,
        "team": 1,
        "latitude": 37.7876146,
        "longitude": -122.390624,
        "slots_available": 0,
        "pokemon": []
    }
    settings.update(values)
    return Gym(settings)


class TestGymEvent(unittest.TestCase):

    def test_gym_id(self):
        gym = generic_gym({'id': 1})
        self.assertTrue(isinstance(gym.gym_id, str))
        self.assertTrue(gym.gym_id == "1")

    def test_team_id(self):
        gym = generic_gym({'team_id': 1})
        self.assertTrue(isinstance(gym.team_id, int))
        self.assertTrue(gym.team_id == 1)

    def test_id(self):
        gym = generic_gym({'id': 12345})
        self.assertTrue(isinstance(gym.id, int))
        self.assertTrue(gym.id == hash("12345"))

    def test_lat(self):
        gym = generic_gym({'latitude': 0})
        self.assertTrue(isinstance(gym.lat, float))
        self.assertTrue(gym.lat == 0.0)

    def test_lng(self):
        gym = generic_gym({'longitude': 0})
        self.assertTrue(isinstance(gym.lng, float))
        self.assertTrue(gym.lng == 0.0)

    def test_gym_name(self):
        gym = generic_gym({'name': "test123"})
        self.assertTrue(isinstance(gym.gym_name, str))
        self.assertTrue(gym.gym_name == "test123")

    def test_gym_description(self):
        gym = generic_gym({'description': "test123"})
        self.assertTrue(isinstance(gym.gym_description, str))
        self.assertTrue(gym.gym_description == "test123")

    def test_gym_image(self):
        gym = generic_gym({'url': "https://someimage.url"})
        self.assertTrue(isinstance(gym.gym_image, str))
        self.assertTrue(gym.gym_image == "https://someimage.url")

    def test_slots_available(self):
        gym = generic_gym({'slots_available': "6"})
        self.assertTrue(isinstance(gym.open_slots, int))
        self.assertTrue(gym.open_slots == 6)

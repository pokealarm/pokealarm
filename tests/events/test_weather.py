# -*- coding: utf-8 -*-

# Standard Library Imports
import unittest
# 3rd Party Imports
# Local Imports
from prototype.events import Weather


def generic_weather(values):
    """ Generate a generic gym, overriding with an specific values. """
    settings = {
        "s2_cell_id": 0,
        "latitude": 37.7876146,
        "longitude": -122.390624,
        "gameplay_weather": 1,
        "severity": 0,
        "world_time": 1
    }
    settings.update(values)
    return Weather(settings)


class TestGymEvent(unittest.TestCase):

    def test_lat(self):
        weather = generic_weather({'latitude': 0})
        self.assertTrue(isinstance(weather.lat, float))
        self.assertTrue(weather.lat == 0.0)

    def test_lng(self):
        weather = generic_weather({'longitude': 0})
        self.assertTrue(isinstance(weather.lng, float))
        self.assertTrue(weather.lng == 0.0)

    def test_s2_cell_id(self):
        weather = generic_weather({'s2_cell_id': "12345"})
        self.assertTrue(isinstance(weather.s2_cell_id, str))
        self.assertTrue(weather.s2_cell_id == "12345")

    def test_weather_id(self):
        weather = generic_weather({'condition': "2"})
        self.assertTrue(isinstance(weather.weather_id, int))
        self.assertTrue(weather.weather_id == 2)

    def test_severity_id(self):
        weather = generic_weather({'severity': "3"})
        self.assertTrue(isinstance(weather.severity_id, int))
        self.assertTrue(weather.severity_id == 3)

    def test_day_or_night_id(self):
        weather = generic_weather({'day': "1"})
        self.assertTrue(isinstance(weather.day_or_night_id, int))
        self.assertTrue(weather.day_or_night_id == 1)

# Standard Library Imports
import calendar
import unittest
from datetime import datetime, timedelta
# 3rd Party Imports
# Local Imports
from pokealarmv4.events import Stop


def generic_stop(values):
    """ Generate a generic stop, overriding with an specific values. """
    settings = {
        "pokestop_id": 0,
        "enabled": "True",
        "latitude": 37.7876146,
        "longitude": -122.390624,
        "last_modified_time": 1572241600,
        "lure_expiration": 1572241600,
        "active_fort_modifier": 0
    }
    settings.update(values)
    return Stop(settings)


class TestStopEvent(unittest.TestCase):

    def test_stop_id(self):
        stop = generic_stop({'pokestop_id': 1})
        self.assertTrue(isinstance(stop.stop_id, str))
        self.assertTrue(stop.stop_id == "1")

    def test_id(self):
        stop = generic_stop({'pokestop_id': 12345})
        self.assertTrue(isinstance(stop.id, int))
        self.assertTrue(stop.id == hash("12345"))

    def test_lat(self):
        stop = generic_stop({'latitude': 0})
        self.assertTrue(isinstance(stop.lat, float))
        self.assertTrue(stop.lat == 0.0)

    def test_lng(self):
        stop = generic_stop({'longitude': 0})
        self.assertTrue(isinstance(stop.lng, float))
        self.assertTrue(stop.lng == 0.0)

    def test_expiration(self):
        stop = generic_stop({})
        self.assertTrue(isinstance(stop.expiration, datetime))

    def test_time_left(self):
        future = datetime.utcnow() + timedelta(seconds=30)
        stop = generic_stop(
            {'lure_expiration': calendar.timegm(future.timetuple())})
        self.assertTrue(isinstance(stop.time_left, float))
        self.assertTrue(0 == int(stop.time_left - 30))

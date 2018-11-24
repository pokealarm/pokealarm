# -*- coding: utf-8 -*-

# Standard Library Imports
import unittest
from datetime import datetime, time, date
# 3rd Party Imports
# Local Imports
from prototype.events import Quest


def generic_quest(values):
    """ Generate a generic quest, overriding with an specific values. """
    settings = {
        "pokestop_id": 0,
        "pokestop_name": "Stop Name",
        "pokestop_url": "http://placehold.it/500x500",
        "latitude": 37.7876146,
        "longitude": -122.390624,
        "quest": "Do Stuff",
        "reward": "Get Stuff",
        "type": 0
    }
    settings.update(values)
    return Quest(settings)


class TestStopEvent(unittest.TestCase):

    def test_lat(self):
        quest = generic_quest({'latitude': 0})
        self.assertTrue(isinstance(quest.lat, float))
        self.assertTrue(quest.lat == 0.0)

    def test_lng(self):
        quest = generic_quest({'longitude': 0})
        self.assertTrue(isinstance(quest.lng, float))
        self.assertTrue(quest.lng == 0.0)

    def test_stop_id(self):
        quest = generic_quest({'pokestop_id': 1})
        self.assertTrue(isinstance(quest.stop_id, str))
        self.assertTrue(quest.stop_id == "1")

    def test_stop_name(self):
        quest = generic_quest({'pokestop_name': 'Stop Name'})
        self.assertTrue(isinstance(quest.stop_name, str))
        self.assertTrue(quest.stop_name == "Stop Name")

    def test_stop_url(self):
        quest = generic_quest({'pokestop_url': 'http://placehold.it/1x1'})
        self.assertTrue(isinstance(quest.stop_image, str))
        self.assertTrue(quest.stop_image == "http://placehold.it/1x1")

    def test_quest(self):
        quest = generic_quest({'quest': 'Do Stuff'})
        self.assertTrue(isinstance(quest.quest, str))
        self.assertTrue(quest.quest == 'Do Stuff')

    def test_reward(self):
        quest = generic_quest({'reward': 'Get Stuff'})
        self.assertTrue(isinstance(quest.reward, str))
        self.assertTrue(quest.reward == 'Get Stuff')

    def test_expire_time(self):
        # Check if it defaults to today at 23:59
        quest = generic_quest([])
        midnight_tonight = datetime.utcfromtimestamp(
            (datetime.combine(date.today(), time(23, 59))
             - datetime(1970, 1, 1)).total_seconds())
        self.assertTrue(isinstance(quest.expire_time, datetime))
        self.assertTrue(quest.expire_time == midnight_tonight)

        # Check if it accepts the webhook field
        midnight_tonight = (datetime.combine(date.today(), time(23, 30))
                            - datetime(1970, 1, 1)).total_seconds()
        quest = generic_quest({'expire_time': midnight_tonight})
        self.assertTrue(isinstance(quest.expire_time, datetime))
        self.assertTrue(quest.expire_time ==
                        datetime.utcfromtimestamp(midnight_tonight))

    def test_type(self):
        quest = generic_quest({'type': 7})
        self.assertTrue(isinstance(quest.reward_type, int))
        self.assertTrue(quest.reward_type == 7)

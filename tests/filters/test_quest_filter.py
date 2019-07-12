import unittest
import PokeAlarm.Filters as Filters
import PokeAlarm.Events as Events
from tests.filters import MockManager, generic_filter_test


class TestQuestFilter(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls._mgr = MockManager()

    @classmethod
    def tearDown(cls):
        pass

    def gen_filter(self, settings):
        """ Generate a generic filter with given settings. """
        return Filters.QuestFilter(self._mgr, "testfilter", settings)

    def gen_event(self, values):
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
        return Events.QuestEvent(settings)

    def test_distance(self):
        # Create the filter
        filt = self.gen_filter(
            {"max_dist": 2000, "min_dist": 400})

        # Test passing
        quest = self.gen_event({})
        for dist in [1000, 800, 600]:
            quest.distance = dist
            self.assertTrue(filt.check_event(quest))

        # Test failing
        quest = self.gen_event({})
        for dist in [0, 300, 3000]:
            quest.distance = dist
            self.assertFalse(filt.check_event(quest))

    def test_missing_info(self):
        # Create the filters
        missing = self.gen_filter(
            {"max_dist": "inf", "is_missing_info": True})
        not_missing = self.gen_filter(
            {"max_dist": "inf", "is_missing_info": False})

        # Test missing
        miss_event = self.gen_event({})
        self.assertTrue(missing.check_event(miss_event))
        self.assertFalse(not_missing.check_event(miss_event))

        # Test not missing
        info_event = self.gen_event({})
        info_event.distance = 1000
        self.assertTrue(not_missing.check_event(info_event))
        self.assertFalse(missing.check_event(info_event))

    @generic_filter_test
    def test_quest_contains(self):
        self.filt = {"quest_contains": ["stuff", "other", "uhh"]}
        self.event_key = "quest"
        self.pass_vals = ["do stuff", "do other things", "uhh stewart"]
        self.fail_vals = ["you know", "I guess", "something"]

    @generic_filter_test
    def test_quest_excludes(self):
        self.filt = {'quest_excludes': ['stuff', 'other', 'uhh']}
        self.event_key = 'quest'
        self.pass_vals = ['something', 'else', 'here']
        self.fail_vals = ['some stuff', 'some other', 'uhh stewart']

    @generic_filter_test
    def test_reward_contains(self):
        self.filt = {'reward_contains': ['stuff', 'other', 'uhh']}
        self.event_key = 'reward'
        self.pass_vals = ['some stuff', 'some other stuff', 'uhh stewart']
        self.fail_vals = ['you know', 'this should', 'fail']

    @generic_filter_test
    def test_reward_excludes(self):
        self.filt = {'reward_excludes': ['stuff', 'other', 'uhh']}
        self.event_key = 'reward'
        self.pass_vals = ['this', 'doesn\'t', 'contain']
        self.fail_vals = ['some stuff', 'some other s', 'uhh stewart']

    @generic_filter_test
    def test_types(self):
        self.filt = {'reward_types': ['Monster Encounter', '1', 2]}
        self.event_key = 'type'
        self.pass_vals = [1, 2, 7]
        self.fail_vals = [0, 3, 4]


if __name__ == '__main__':
    unittest.main()

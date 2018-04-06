from datetime import datetime, timedelta
import time
import unittest
import PokeAlarm.Filters as Filters
import PokeAlarm.Events as Events
from tests.filters import MockManager, generic_filter_test


class TestRaidFilter(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls._mgr = MockManager()

    @classmethod
    def tearDown(cls):
        pass

    def gen_filter(self, settings):
        """ Generate a generic filter with given settings. """
        return Filters.RaidFilter(self._mgr, "testfilter", settings)

    def gen_event(self, values):
        """ Generate a generic raid, overriding with an specific values. """
        settings = {
            "gym_id": "OWNmOTFmMmM0YTY3NGQwYjg0Y2I1N2JlZjU4OWRkMTYuMTY=",
            "url": "???",
            "name": "Unknown",
            "description": "???",
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
        return Events.RaidEvent(settings)

    @generic_filter_test
    def test_monster_id(self):
        self.filt = {"monsters": [382, "383", "Rayquaza"]}
        self.event_key = "pokemon_id"
        self.pass_vals = [382, 383, 384]
        self.fail_vals = [20, 150, 301]

    @generic_filter_test
    def test_monsters_exclude(self):
        self.filt = {"monsters_exclude": [382, "383", "Rayquaza"]}
        self.event_key = "pokemon_id"
        self.pass_vals = [20, 150, 301]
        self.fail_vals = [382, 383, 384]

    @generic_filter_test
    def test_quick_moves(self):
        self.filt = {"quick_moves": [225, "88", "Present"]}
        self.event_key = "move_1"
        self.pass_vals = [225, 88, 291]
        self.fail_vals = [200, 201, 202]

    @generic_filter_test
    def test_charge_moves(self):
        self.filt = {"charge_moves": [283, "14", "Solar Beam"]}
        self.event_key = "move_2"
        self.pass_vals = [283, 14, 116]
        self.fail_vals = [200, 201, 202]

    @generic_filter_test
    def test_raid_lvl(self):
        self.filt = {"min_raid_lvl": 2, "max_raid_lvl": 4}
        self.event_key = "level"
        self.pass_vals = [2, 3, 4]
        self.fail_vals = [1, 5]

    @generic_filter_test
    def test_gym_name_contains(self):
        self.filt = {"gym_name_contains": ["pass"]}
        self.event_key = "name"
        self.pass_vals = ["pass1", "2pass", "3pass3"]
        self.fail_vals = ["fail1", "failpas", "pasfail"]

    @generic_filter_test
    def test_gym_name_excludes(self):
        self.filt = {"gym_name_excludes": ["fail"]}
        self.event_key = "name"
        self.pass_vals = ["pass1", "2pass", "3pass3"]
        self.fail_vals = ["fail1", "failpas", "pasfail"]

    @generic_filter_test
    def test_park_contains(self):
        self.filt = {"park_contains": ["pass"]}
        self.event_key = "park"
        self.pass_vals = ["pass1", "2pass", "3pass3"]
        self.fail_vals = ["fail1", "failpas", "pasfail"]

    @generic_filter_test
    def test_current_teams(self):
        self.filt = {"current_teams": [1, "2", "Instinct"]}
        self.event_key = "team"
        self.pass_vals = [1, 2, 3]
        self.fail_vals = [0]

    def test_sponsored(self):
        # Create the filters
        filter1 = self.gen_filter({"sponsored": False})
        filter2 = self.gen_filter({"sponsored": True})

        # Generate events
        not_sponsored = self.gen_event({"sponsor": 0})
        sponsored = self.gen_event({"sponsor": 4})

        # Test passing events
        self.assertTrue(filter1.check_event(not_sponsored))
        self.assertTrue(filter2.check_event(sponsored))

        # Test failing events
        self.assertFalse(filter2.check_event(not_sponsored))
        self.assertFalse(filter1.check_event(sponsored))

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

    def test_raid_distance(self):
        # Create the filter
        filt = self.gen_filter(
            {"max_dist": 2000, "min_dist": 400})

        # Test passing
        egg = self.gen_event({})
        for dist in [1000, 800, 600]:
            egg.distance = dist
            self.assertTrue(filt.check_event(egg))

        # Test failing
        egg = self.gen_event({})
        for dist in [0, 300, 3000]:
            egg.distance = dist
            self.assertFalse(filt.check_event(egg))

    @generic_filter_test
    def test_cp(self):
        self.filt = {'min_cp': 5000, 'max_cp': 9000}
        self.event_key = "cp"
        self.pass_vals = [5000, 8000, 9000]
        self.fail_vals = [4999, 9001, 999999]

    def test_time_left(self):
        # Create the filter
        filt = self.gen_filter(
            {'min_time_left': 1000, 'max_time_left': 8000})

        # Test passing
        for s in [2000, 4000, 6000]:
            d = (datetime.now() + timedelta(seconds=s))
            t = time.mktime(d.timetuple())
            event = self.gen_event({"end": t})
            self.assertTrue(filt.check_event(event))

        # Test failing
        for s in [200, 999, 8001]:
            d = (datetime.now() + timedelta(seconds=s))
            t = time.mktime(d.timetuple())
            event = self.gen_event({"end": t})
            self.assertFalse(filt.check_event(event))


if __name__ == '__main__':
    unittest.main()

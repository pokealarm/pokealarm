from datetime import datetime, timedelta
import time
import unittest
import PokeAlarm.Filters as Filters
import PokeAlarm.Events as Events
from tests.filters import MockManager


class TestEggFilter(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls._mgr = MockManager()

    @classmethod
    def tearDown(cls):
        pass

    def gen_filter(self, settings):
        """ Generate a generic filter with given settings. """
        return Filters.EggFilter(self._mgr, "testfilter", settings)

    def gen_event(self, values):
        """ Generate a generic egg, overriding with an specific values. """
        settings = {
            "gym_id": "OWNmOTFmMmM0YTY3NGQwYjg0Y2I1N2JlZjU4OWRkMTYuMTY=",
            "url": "???",
            "name": "unknown",
            "description": "???",
            "start": 1499244052,
            "end": 1499246052,
            "level": 5,
            "latitude": 37.7876146,
            "longitude": -122.390624,
            "sponsor": None,
            "park": None
        }
        settings.update(values)
        return Events.EggEvent(settings)

    def test_egg_lvl(self):
        # Create the filter
        egg_filter = self.gen_filter({"min_egg_lvl": 2, "max_egg_lvl": 4})

        # Test passing
        for lvl in [2, 3, 4]:
            event = self.gen_event({"level": lvl})
            self.assertTrue(egg_filter.check_event(event))

        # Test failing
        for lvl in [1, 5]:
            event = self.gen_event({"level": lvl})
            self.assertFalse(egg_filter.check_event(event))

    def test_gym_name_contains(self):
        # Create the filter
        egg_filter = self.gen_filter({"gym_name_contains": ["pass"]})

        # Test passing
        for name in ["pass1", "2pass", "3pass"]:
            event = self.gen_event({"name": name})
            self.assertTrue(egg_filter.check_event(event))

        # Test failing
        for name in ["fail1", "failpas", "pasfail"]:
            event = self.gen_event({"name": name})
            self.assertFalse(egg_filter.check_event(event))

    def test_gym_name_excludes(self):
        # Create the filter
        egg_filter = self.gen_filter({"gym_name_excludes": ["fail"]})

        # Test passing
        for name in ["pass1", "2pass", "3pass3"]:
            event = self.gen_event({"name": name})
            self.assertTrue(egg_filter.check_event(event))

        # Test failing
        for name in ["fail1", "failpass", "passfail"]:
            event = self.gen_event({"name": name})
            self.assertFalse(egg_filter.check_event(event))

    def test_park_contains(self):
        # Create the filter
        egg_filter = self.gen_filter({"park_contains": ["pass"]})

        # Test passing
        for name in ["pass1", "2pass", "3pass3"]:
            event = self.gen_event({"park": name})
            self.assertTrue(egg_filter.check_event(event))

        # Test failing
        for name in ["fail1", "failpas", "pasfail"]:
            event = self.gen_event({"park": name})
            self.assertFalse(egg_filter.check_event(event))

    def test_current_teams(self):
        # Create the filter
        egg_filter = self.gen_filter({"current_teams": [1, "2", "Instinct"]})

        # Test passing
        for team in [1, 2, 3]:
            event = self.gen_event({"team": team})
            self.assertTrue(egg_filter.check_event(event))

        # Test failing
        for team in [0]:
            event = self.gen_event({"team": team})
            self.assertFalse(egg_filter.check_event(event))

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

    def test_egg_distance(self):
        # Create the filter
        egg_filter = self.gen_filter(
            {"max_dist": 2000, "min_dist": 400})

        # Test passing
        egg = self.gen_event({})
        for dist in [1000, 800, 600]:
            egg.distance = dist
            self.assertTrue(egg_filter.check_event(egg))

        # Test failing
        egg = self.gen_event({})
        for dist in [0, 300, 3000]:
            egg.distance = dist
            self.assertFalse(egg_filter.check_event(egg))

    def test_time_left(self):
        # Create the filter
        egg_filter = self.gen_filter(
            {'min_time_left': 1000, 'max_time_left': 8000})

        # Test passing
        for s in [2000, 4000, 6000]:
            d = (datetime.now() + timedelta(seconds=s))
            t = time.mktime(d.timetuple())
            event = self.gen_event({"start": t})
            self.assertTrue(egg_filter.check_event(event))

        # Test failing
        for s in [200, 999, 8001]:
            d = (datetime.now() + timedelta(seconds=s))
            t = time.mktime(d.timetuple())
            event = self.gen_event({"start": t})
            self.assertFalse(egg_filter.check_event(event))


if __name__ == '__main__':
    unittest.main()

from datetime import datetime, timedelta
import time
import unittest
import PokeAlarm.Filters as Filters
import PokeAlarm.Events as Events
from PokeAlarm.Geofence import load_geofence_file
from tests.filters import MockManager, generic_filter_test


class TestGruntFilter(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls._mgr = MockManager()

    @classmethod
    def tearDown(cls):
        pass

    def gen_filter(self, settings):
        """ Generate a generic filter with given settings. """
        return Filters.GruntFilter(self._mgr, "testfilter", settings)

    def gen_event(self, values):
        """
        Generate a generic invasion, overriding with an specific values.
        """
        settings = {
            "pokestop_id": 0,
            "enabled": "True",
            "latitude": 37.7876146,
            "longitude": -122.390624,
            "last_modified_time": 1572241600,
            "incident_expiration": 1572241600,
            "grunt_type": 6
        }
        settings.update(values)
        return Events.GruntEvent(settings)

    def test_distance(self):
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

    def test_time_left(self):
        # Create the filter
        filt = self.gen_filter(
            {'min_time_left': 1000, 'max_time_left': 8000})

        # Test passing
        for s in [2000, 4000, 6000]:
            d = (datetime.now() + timedelta(seconds=s))
            t = time.mktime(d.timetuple())
            event = self.gen_event({"incident_expiration": t})
            self.assertTrue(filt.check_event(event))

        # Test failing
        for s in [200, 999, 8001]:
            d = (datetime.now() + timedelta(seconds=s))
            t = time.mktime(d.timetuple())
            event = self.gen_event({"incident_expiration": t})
            self.assertFalse(filt.check_event(event))

    def test_geofences(self):
        # Create the filter
        filt = self.gen_filter(
            {'geofences': ['NewYork']})

        geofences_ref = load_geofence_file("tests/filters/test_geofences.txt")
        filt._check_list[0].override_geofences_ref(geofences_ref)

        # Test passing
        for (lat, lng) in [(40.689256, -74.044510), (40.630720, -74.087673),
                           (40.686905, -73.853559)]:
            event = self.gen_event({"latitude": lat,
                                    "longitude": lng})
            self.assertTrue(filt.check_event(event))

        # Test failing
        for (lat, lng) in [(38.920936, -77.047371), (48.858093, 2.294694),
                           (-37.809022, 144.959003)]:
            event = self.gen_event({"latitude": lat,
                                    "longitude": lng})
            self.assertFalse(filt.check_event(event))

    @generic_filter_test
    def test_grunt_type(self):
        # Dragon, Ghost - "Dragon" should allow both m&f versions (12 & 13)
        self.filt = {'grunt_types': ["Dragon", 8]}
        self.event_key = 'grunt_type'
        self.pass_vals = [12, 8, 13]
        self.fail_vals = [0, 1, 5, 1111]

    @generic_filter_test
    def test_grunt_gender(self):
        self.filt = {'grunt_genders': ['male', 1, '1']}
        self.event_key = 'grunt_type'
        self.pass_vals = [7, 9]  # 7 = Bug Male, 9 = Ghost Male
        self.fail_vals = [6, 8]  # 6 = Bug Female, 8 = Ghost Female


if __name__ == '__main__':
    unittest.main()

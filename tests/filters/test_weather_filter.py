import unittest
import PokeAlarm.Filters as Filters
import PokeAlarm.Events as Events
from tests.filters import MockManager, generic_filter_test


class TestWeatherFilter(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls._mgr = MockManager()

    @classmethod
    def tearDown(cls):
        pass

    def gen_filter(self, settings):
        return Filters.WeatherFilter(self._mgr, "testfilter", settings)

    # Create a generic weather change, overriding with specific values
    def gen_event(self, values):
        weather_settings = {
            "s2_cell_id": 0,
            "latitude": 37.7876146,
            "longitude": -122.390624,
            "gameplay_weather": 1,
            "severity": 0,
            "world_time": 1
        }
        weather_settings.update(values)
        return Events.WeatherEvent(weather_settings)

    def test_distance(self):
        # Create filter
        filt = self.gen_filter(
            {'min_dist': 5, 'max_dist': 2000})

        # Test passing
        weather = self.gen_event({})
        for dist in [5, 2000, 1000]:
            weather.distance = dist
            self.assertTrue(filt.check_event(weather))

        # Test failing
        weather = self.gen_event({})
        for dist in [4, 2001, 9999]:
            weather.distance = dist
            self.assertFalse(filt.check_event(weather))

    @generic_filter_test
    def test_severity(self):
        self.filt = {'severity': [1, "Extreme"]}
        self.event_key = 'severity'
        self.pass_vals = [1]
        self.fail_vals = [0]

    @generic_filter_test
    def test_weather(self):
        self.filt = {'weather': [1, 5, "Cloudy"]}
        self.event_key = 'gameplay_weather'
        self.pass_vals = [1]
        self.fail_vals = [2]

    @generic_filter_test
    def test_day_or_night(self):
        self.filt = {'day_or_night': ['Day']}
        self.event_key = 'world_time'
        self.pass_vals = [1]
        self.fail_vals = [2]


if __name__ == '__main__':
    unittest.main()

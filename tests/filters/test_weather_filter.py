import unittest
import PokeAlarm.Filters as Filters
import PokeAlarm.Events as Events


class TestWeatherFilter(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_distance(self):
        weather_event = Events.WeatherEvent(generate_weather({}))
        settings = {'min_dist': 5, 'max_dist': 2000}
        weather_filter = Filters.WeatherFilter('distance_filter', settings)
        for i in [5, 2000, 1000]:
            weather_event.distance = i
            self.assertTrue(weather_filter.check_event(weather_event))

        settings2 = {'min_dist': 100, 'max_dist': 5000}
        weather_filter2 = Filters.WeatherFilter('distance_filter_2', settings2)
        for i in [99, 5001, 9999]:
            weather_event.distance = i
            self.assertFalse(weather_filter2.check_event(weather_event))

    def test_custom_dts(self):
        settings = {'custom_dts': {
            'key1': 'value1',
            'I\'m a goofy': 'goober yeah!'
        }}
        weather_filter = Filters.WeatherFilter('custom_dts_filter', settings)
        self.assertTrue(weather_filter.check_event(create_event({})))

    # Unsure if this webhook will send prbable missing info later
    # def test_missing_info(self):
    #     settings = {'is_missing_info': False, 'max_dist': 500}
    #     weather_filter = Filters.WeatherFilter('missing_info_filter', settings)
    #     weather_event = Events.WeatherEvent(generate_weather({}))
    #     self.assertFalse(weather_filter.check_event(weather_event))
    #     for i in [0, 500]:
    #         weather_event.distance = i
    #         self.assertTrue(weather_filter.check_event(weather_event))
    #     weather_event.distance = 'Unknown'
    #     self.assertFalse(weather_filter.check_event(weather_event))

    def test_alert(self):
        settings = {'alert': [1, "Extreme"]}
        weather_filter = Filters.WeatherFilter('alert_filter', settings)
        weather_event1 = Events.WeatherEvent(generate_weather({'severity': 1}))
        self.assertTrue(weather_filter.check_event(weather_event1))
        weather_event2 = Events.WeatherEvent(generate_weather({'severity': 0}))
        self.assertFalse(weather_filter.check_event(weather_event2))

    def test_weather(self):
        settings = {'weather': [1, 5, "Cloudy"]}
        weather_filter = Filters.WeatherFilter('weather_filter', settings)
        weather_event1 = Events.WeatherEvent(generate_weather(
            {'gameplay_weather': 1}))
        self.assertTrue(weather_filter.check_event(weather_event1))
        weather_event2 = Events.WeatherEvent(generate_weather(
            {'gameplay_weather': 2}))
        self.assertFalse(weather_filter.check_event(weather_event2))

    def test_day_or_night(self):
        settings = {'day_or_night': ['Day']}
        weather_filter = Filters.WeatherFilter('weather_filter', settings)
        weather_event1 = Events.WeatherEvent(generate_weather(
            {'world_time': 1}))
        self.assertTrue(weather_filter.check_event(weather_event1))
        weather_event2 = Events.WeatherEvent(generate_weather(
            {'world_time': 2}))
        self.assertFalse(weather_filter.check_event(weather_event2))


# Create a generic weather change, overriding with specific values
def generate_weather(values):
    weather = {
        "s2_cell_id": 0,
        "latitude": 37.7876146,
        "longitude": -122.390624,
        "gameplay_weather": 1,
        "severity": 0,
        "world_time": 1
    }
    weather.update(values)
    return weather


# Create the event and change default values
def create_event(items_to_change):
    return Events.WeatherEvent(generate_weather(items_to_change))


if __name__ == '__main__':
    unittest.main()

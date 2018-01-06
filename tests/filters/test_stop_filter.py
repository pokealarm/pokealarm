import unittest
import PokeAlarm.Filters as Filters
import PokeAlarm.Events as Events


class TestStopFilter(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_distance(self):
        stop_event = Events.StopEvent(generate_stop({}))
        settings = {'min_dist': 5, 'max_dist': 2000}
        stop_filter = Filters.StopFilter('distance_filter', settings)
        for i in [5, 2000, 1000]:
            stop_event.distance = i
            self.assertTrue(stop_filter.check_event(stop_event))

        settings2 = {'min_dist': 100, 'max_dist': 5000}
        stop_filter2 = Filters.StopFilter('distance_filter_2', settings2)
        for i in [99, 5001, 9999]:
            stop_event.distance = i
            self.assertFalse(stop_filter2.check_event(stop_event))

    def test_custom_dts(self):
        settings = {'custom_dts': {'key1': 'value1', 'I\'m a goofy': 'goober yeah!'}}
        stop_filter = Filters.StopFilter('custom_dts_filter', settings)
        self.assertTrue(stop_filter.check_event(create_event({})))

    def test_missing_info(self):
        settings = {'is_missing_info': False, 'max_dist': 500}
        stop_filter = Filters.StopFilter('missing_info_filter', settings)
        stop_event = Events.StopEvent(generate_stop({}))
        self.assertFalse(stop_filter.check_event(stop_event))
        for i in [0, 500]:
            stop_event.distance = i
            self.assertTrue(stop_filter.check_event(stop_event))
        stop_event.distance = 'Unknown'
        self.assertFalse(stop_filter.check_event(stop_event))


# Create a generic stop, overriding with an specific values
def generate_stop(values):
    stop = {
        "pokestop_id": 0,
        "enabled": "True",
        "latitude": 37.7876146,
        "longitude": -122.390624,
        "last_modified_time": 1572241600,
        "lure_expiration": 1572241600,
        "active_fort_modifier": 0
    }
    stop.update(values)
    return stop


# Create the event and change default values
def create_event(items_to_change):
    return Events.StopEvent(generate_stop(items_to_change))


if __name__ == '__main__':
    unittest.main()

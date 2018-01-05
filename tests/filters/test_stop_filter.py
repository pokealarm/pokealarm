import unittest
import PokeAlarm.Filters as Filters
import PokeAlarm.Events as Events


class TestStopFilter(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_distance(self):
        settings = {'min_dist': 0, 'max_dist': 100}
        stop_filter = Filters.StopFilter('distance_filter', settings)
        self.assertTrue(stop_filter.check_event(create_event({})))

    # def test_geofences(self):

    # def test_custom_dts(self):

    # def test_missing_info(self):


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

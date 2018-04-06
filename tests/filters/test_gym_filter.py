import unittest
import PokeAlarm.Filters as Filters
import PokeAlarm.Events as Events
from tests.filters import MockManager, generic_filter_test


class TestGymFilter(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls._mgr = MockManager()

    @classmethod
    def tearDown(cls):
        pass

    def gen_filter(self, settings):
        """ Generate a gym filter with given settings. """
        return Filters.GymFilter(self._mgr, "testfilter", settings)

    def gen_event(self, values):
        """ Generate a generic gym, overriding with an specific values. """
        settings = {
            "id": "OWNmOTFmMmM0YTY3NGQwYjg0Y2I1N2JlZjU4OWRkMTYuMTY=",
            "url": "???",
            "name": "unknown",
            "description": "???",
            "team": 1,
            "latitude": 37.7876146,
            "longitude": -122.390624,
            "pokemon": [{
                "num_upgrades": 0,
                "move_1": 234,
                "move_2": 99,
                "additional_cp_multiplier": 0,
                "iv_defense": 11,
                "weight": 14.138585090637207,
                "pokemon_id": 63,
                "stamina_max": 46,
                "cp_multiplier": 0.39956727623939514,
                "height": 0.7160492539405823,
                "stamina": 46,
                "pokemon_uid": 9278614152997308833,
                "deployment_time": 1506894280,
                "iv_attack": 12,
                "trainer_name": "SportyGator",
                "trainer_level": 18,
                "cp": 138,
                "iv_stamina": 8,
                "cp_decayed": 125
            }, {
                "num_upgrades": 0,
                "move_1": 234,
                "move_2": 87,
                "additional_cp_multiplier": 0,
                "iv_defense": 12,
                "weight": 3.51259708404541,
                "pokemon_id": 36,
                "stamina_max": 250,
                "cp_multiplier": 0.6121572852134705,
                "height": 1.4966495037078857,
                "stamina": 250,
                "pokemon_uid": 6103380929145641793,
                "deployment_time": 1506894733,
                "iv_attack": 5,
                "trainer_name": "Meckelangelo",
                "trainer_level": 22,
                "cp": 1353,
                "iv_stamina": 15,
                "cp_decayed": 1024
            }, {
                "num_upgrades": 9,
                "move_1": 224,
                "move_2": 32,
                "additional_cp_multiplier": 0.06381925195455551,
                "iv_defense": 13,
                "weight": 60.0,
                "pokemon_id": 31,
                "stamina_max": 252,
                "cp_multiplier": 0.5974000096321106,
                "height": 1.0611374378204346,
                "stamina": 252,
                "pokemon_uid": 3580711458547635980,
                "deployment_time": 1506894763,
                "iv_attack": 10,
                "trainer_name": "Plaidflamingo",
                "trainer_level": 23,
                "cp": 1670,
                "iv_stamina": 11,
                "cp_decayed": 1435
            }]
        }
        settings.update(values)
        return Events.GymEvent(settings)

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
    def test_gym_slots(self):
        self.filt = {"min_slots": 2, "max_slots": 4}
        self.event_key = "slots_available"
        self.pass_vals = [2, 3, 4]
        self.fail_vals = [0, 1, 5]

    @generic_filter_test
    def test_new_teams(self):
        self.filt = {"new_teams": [1, "2", "Instinct"]}
        self.event_key = "team"
        self.pass_vals = [1, 2, 3]
        self.fail_vals = [0]

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

    def test_gym_distance(self):
        # Create the filter
        filt = self.gen_filter(
            {"max_dist": 2000, "min_dist": 400})

        # Test passing
        gym = self.gen_event({})
        for dist in [1000, 800, 600]:
            gym.distance = dist
            self.assertTrue(filt.check_event(gym))

        # Test failing
        gym = self.gen_event({})
        for dist in [0, 300, 3000]:
            gym.distance = dist
            self.assertFalse(filt.check_event(gym))


if __name__ == '__main__':
    unittest.main()

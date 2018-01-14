import unittest
import PokeAlarm.Filters as Filters
import PokeAlarm.Events as Events


class TestGymFilter(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_gym_names(self):
        # Create the filters
<<<<<<< HEAD
        settings = {"gym_name_contains": ["pass"]}
=======
        settings = {"gym_name_matches": ["pass.\Z"]}
>>>>>>> f93f49fde6df6f2f9398d44e52a545a3dc6f2921
        gym_filter = Filters.GymFilter('filter1', settings)

        # Generate events that should pass
        pass1 = Events.GymEvent(generate_gym({"name": "pass1"}))
<<<<<<< HEAD
        pass2 = Events.GymEvent(generate_gym({"name": "2pass"}))
        pass3 = Events.GymEvent(generate_gym({"name": "3pass3"}))
=======
        pass2 = Events.GymEvent(generate_gym({"name": "pass2"}))
        pass3 = Events.GymEvent(generate_gym({"name": "pass3"}))
>>>>>>> f93f49fde6df6f2f9398d44e52a545a3dc6f2921
        # Test passing events
        for e in [pass1, pass2, pass3]:
            self.assertTrue(gym_filter.check_event(e))

        # Generate events that should fail
        fail1 = Events.GymEvent(generate_gym({"name": "fail1"}))
<<<<<<< HEAD
        fail2 = Events.GymEvent(generate_gym({"name": "failpas"}))
        fail3 = Events.GymEvent(generate_gym({"name": "pasfail"}))

        # Test failing events
        for e in [fail1, fail2, fail3]:
            self.assertFalse(gym_filter.check_event(e))

    def test_gym_guards(self):
        # Create the filters
        settings = {"min_slots": 2, "max_slots": 4}
        gym_filter = Filters.GymFilter('filter1', settings)

        # Generate events that should pass
        pass1 = Events.GymEvent(generate_gym({"slots_available": 2}))
        pass2 = Events.GymEvent(generate_gym({"slots_available": 3}))
        pass3 = Events.GymEvent(generate_gym({"slots_available": 4}))
        # Test passing events
        for e in [pass1, pass2, pass3]:
            self.assertTrue(gym_filter.check_event(e))

        # Generate events that should fail
        fail1 = Events.GymEvent(generate_gym({"slots_available": 0}))
        fail2 = Events.GymEvent(generate_gym({"slots_available": 1}))
        fail3 = Events.GymEvent(generate_gym({"slots_available": 5}))
=======
        fail2 = Events.GymEvent(generate_gym({"name": "failpass"}))
        fail3 = Events.GymEvent(generate_gym({"name": "passfail"}))
>>>>>>> f93f49fde6df6f2f9398d44e52a545a3dc6f2921

        # Test failing events
        for e in [fail1, fail2, fail3]:
            self.assertFalse(gym_filter.check_event(e))

    def test_gym_team(self):
        # Create the filters
        settings = {"new_teams": [1, "2", "Instinct"]}
        gym_filter = Filters.GymFilter('filter1', settings)

        # Generate events that should pass
        pass1 = Events.GymEvent(generate_gym({"team": 1}))
        pass2 = Events.GymEvent(generate_gym({"team": 2}))
        pass3 = Events.GymEvent(generate_gym({"team": 3}))
        # Test passing events
        for e in [pass1, pass2, pass3]:
            self.assertTrue(gym_filter.check_event(e))

        # Generate events that should fail
        fail1 = Events.GymEvent(generate_gym({"team": 0}))

        # Test failing events
        for e in [fail1]:
            self.assertFalse(gym_filter.check_event(e))

    def test_missing_info1(self):
        # Create the filters
        settings = {"max_dist": "inf", "is_missing_info": True}
        gym_filter = Filters.GymFilter('filter1', settings)

        # Generate events that should pass
        pass1 = Events.GymEvent(generate_gym({"dist": "Unknown"}))
        # Test passing events
        for e in [pass1]:
            self.assertTrue(gym_filter.check_event(e))

    def test_missing_info2(self):
        # Create the filters
        settings = {"max_dist": "inf", "is_missing_info": False}
        gym_filter = Filters.GymFilter('filter1', settings)

        # Generate events that should pass
        pass1 = Events.GymEvent(generate_gym({}))
        pass1.distance = 1000

        # Test passing events
        for e in [pass1]:
            self.assertTrue(gym_filter.check_event(e))

    def test_egg_distance(self):
        # Create the filters
        settings = {"max_dist": "2000", "min_dist": "400"}
        gym_filter = Filters.GymFilter('filter1', settings)

        # Generate events that should pass
        pass1 = Events.GymEvent(generate_gym({}))
        pass1.distance = 1000
        pass2 = Events.GymEvent(generate_gym({}))
        pass2.distance = 800
        pass3 = Events.GymEvent(generate_gym({}))
        pass3.distance = 600

        # Test passing events
        for e in [pass1]:
            self.assertTrue(gym_filter.check_event(e))

        # Generate events that should fail
        fail1 = Events.GymEvent(generate_gym({}))
        fail1.distance = 3000
        fail2 = Events.GymEvent(generate_gym({}))
        fail2.distance = 300
        fail3 = Events.GymEvent(generate_gym({}))
        fail3.distance = 0

        # Test failing events
        for e in [fail1, fail2, fail3]:
            self.assertFalse(gym_filter.check_event(e))

    def test_custom_dts(self):
        # Create the filters
        settings = {"custom_dts": {"key1": "pass1"}}
        gym_filter = Filters.GymFilter('filter1', settings)

        # Generate events that should pass
        pass1 = Events.GymEvent(generate_gym({}))
        # Test passing events
        for e in [pass1]:
            self.assertTrue(gym_filter.check_event(e))


# Create a generic gym, overriding with an specific values
def generate_gym(values):
    gym = {
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
    gym.update(values)
    return gym


if __name__ == '__main__':
    unittest.main()

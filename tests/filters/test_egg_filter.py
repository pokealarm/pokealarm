from datetime import datetime, timedelta
import time
import unittest
import PokeAlarm.Filters as Filters
import PokeAlarm.Events as Events


class TestEggFilter(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_egg_lvl(self):
        # Create the filters
        settings = {"min_egg_lvl": 2, "max_egg_lvl": 4}
        egg_filter = Filters.EggFilter('filter1', settings)

        # Generate events that should pass
        pass1 = Events.EggEvent(generate_egg({"level": 2}))
        pass2 = Events.EggEvent(generate_egg({"level": 3}))
        pass3 = Events.EggEvent(generate_egg({"level": 4}))
        # Test passing events
        for e in [pass1, pass2, pass3]:
            self.assertTrue(egg_filter.check_event(e))

        # Generate events that should fail
        fail1 = Events.EggEvent(generate_egg({"level": 1}))
        fail2 = Events.EggEvent(generate_egg({"level": 5}))

        # Test failing events
        for e in [fail1, fail2]:
            self.assertFalse(egg_filter.check_event(e))

    def test_gym_names(self):
        # Create the filters
        settings = {"gym_name_contains": ["pass"]}
        egg_filter = Filters.EggFilter('filter1', settings)

        # Generate events that should pass
        # Generate events that should pass
        pass1 = Events.EggEvent(generate_egg({"name": "pass1"}))
        pass2 = Events.EggEvent(generate_egg({"name": "2pass"}))
        pass3 = Events.EggEvent(generate_egg({"name": "3pass3"}))

        # Test passing events
        for e in [pass1, pass2, pass3]:
            self.assertTrue(egg_filter.check_event(e))

        # Generate events that should fail
        fail1 = Events.EggEvent(generate_egg({"name": "fail1"}))
        fail2 = Events.EggEvent(generate_egg({"name": "failpas"}))
        fail3 = Events.EggEvent(generate_egg({"name": "pasfail"}))

        # Test failing events
        for e in [fail1, fail2, fail3]:
            self.assertFalse(egg_filter.check_event(e))

    def test_current_team(self):
        # Create the filters
        settings = {"current_teams": [1, "2", "Instinct"]}
        egg_filter = Filters.EggFilter('filter1', settings)

        # Generate events that should pass
        pass1 = Events.EggEvent(generate_egg({"team": 1}))
        pass2 = Events.EggEvent(generate_egg({"team": 2}))
        pass3 = Events.EggEvent(generate_egg({"team": 3}))
        # Test passing events
        for e in [pass1, pass2, pass3]:
            self.assertTrue(egg_filter.check_event(e))

        # Generate events that should fail
        fail1 = Events.EggEvent(generate_egg({"team": 0}))

        # Test failing events
        for e in [fail1]:
            self.assertFalse(egg_filter.check_event(e))

    def test_missing_info1(self):
        # Create the filters
        settings = {"max_dist": "inf", "is_missing_info": True}
        egg_filter = Filters.EggFilter('filter1', settings)

        # Generate events that should pass
        pass1 = Events.EggEvent(generate_egg({"dist": "Unknown"}))
        # Test passing events
        for e in [pass1]:
            self.assertTrue(egg_filter.check_event(e))

    def test_missing_info2(self):
        # Create the filters
        settings = {"max_dist": "inf", "is_missing_info": False}
        egg_filter = Filters.EggFilter('filter1', settings)

        # Generate events that should pass
        pass1 = Events.EggEvent(generate_egg({}))
        pass1.distance = 1000

        # Test passing events
        for e in [pass1]:
            self.assertTrue(egg_filter.check_event(e))

    def test_egg_distance(self):
        # Create the filters
        settings = {"max_dist": "2000", "min_dist": "400"}
        egg_filter = Filters.EggFilter('filter1', settings)

        # Generate events that should pass
        pass1 = Events.EggEvent(generate_egg({}))
        pass1.distance = 1000
        pass2 = Events.EggEvent(generate_egg({}))
        pass2.distance = 800
        pass3 = Events.EggEvent(generate_egg({}))
        pass3.distance = 600

        # Test passing events
        for e in [pass1]:
            self.assertTrue(egg_filter.check_event(e))

        # Generate events that should fail
        fail1 = Events.EggEvent(generate_egg({}))
        fail1.distance = 3000
        fail2 = Events.EggEvent(generate_egg({}))
        fail2.distance = 300
        fail3 = Events.EggEvent(generate_egg({}))
        fail3.distance = 0

        # Test failing events
        for e in [fail1, fail2, fail3]:
            self.assertFalse(egg_filter.check_event(e))

    def test_custom_dts(self):
        # Create the filters
        settings = {"custom_dts": {"key1": "pass1"}}
        egg_filter = Filters.EggFilter('filter1', settings)

        # Generate events that should pass
        pass1 = Events.EggEvent(generate_egg({}))

        # Test passing events
        for e in [pass1]:
            self.assertTrue(egg_filter.check_event(e))

    def test_time_left(self):
        # Create the filters
        settings = {'min_time_to_hatch': 1000, 'max_time_to_hatch': 8000}
        egg_filter = Filters.EggFilter('time_filter', settings)

        # Test events that should pass
        for s in [2000, 4000, 6000]:
            d = (datetime.now() + timedelta(seconds=s))
            t = time.mktime(d.timetuple())
            event = Events.EggEvent(generate_egg({"start": t}))
            self.assertTrue(egg_filter.check_event(event))

        # Test events that should fail
        for s in [200, 999, 8001]:
            d = (datetime.now() + timedelta(seconds=s))
            t = time.mktime(d.timetuple())
            event = Events.EggEvent(generate_egg({"start": t}))
            self.assertFalse(egg_filter.check_event(event))


# Create a generic egg, overriding with an specific values
def generate_egg(values):
    egg = {
        "gym_id": "OWNmOTFmMmM0YTY3NGQwYjg0Y2I1N2JlZjU4OWRkMTYuMTY=",
        "url": "???",
        "name": "unknown",
        "description": "???",
        "start": 1499244052,
        "end": 1499246052,
        "level": 5,
        "latitude": 37.7876146,
        "longitude": -122.390624
    }
    egg.update(values)
    return egg


if __name__ == '__main__':
    unittest.main()

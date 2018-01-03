import unittest
import PokeAlarm.Filters as Filters
import PokeAlarm.Events as Events


class TestRaidFilter(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_monster_id(self):
        # Create the filters
        settings = {"monsters": [382, "383", "Rayquaza"]}
        raid_filter = Filters.RaidFilter('filter1', settings)

        # Generate events that should pass
        pass1 = Events.RaidEvent(generate_raid({"pokemon_id": 382}))
        pass2 = Events.RaidEvent(generate_raid({"pokemon_id": 383}))
        pass3 = Events.RaidEvent(generate_raid({"pokemon_id": 384}))
        # Test passing events
        for e in [pass1, pass2, pass3]:
            self.assertTrue(raid_filter.check_event(e))

        # Generate events that should fail
        fail1 = Events.RaidEvent(generate_raid({"pokemon_id": 20}))
        fail2 = Events.RaidEvent(generate_raid({"pokemon_id": 150}))
        fail3 = Events.RaidEvent(generate_raid({"pokemon_id": 301}))

        # Test failing events
        for e in [fail1, fail2, fail3]:
            self.assertFalse(raid_filter.check_event(e))

    def test_quick_move(self):
        # Create the filters
        settings = {"quick_moves": [225, "88", "Present"]}
        raid_filter = Filters.RaidFilter('filter1', settings)

        # Generate events that should pass
        pass1 = Events.RaidEvent(generate_raid({"move_1": 225}))
        pass2 = Events.RaidEvent(generate_raid({"move_1": 88}))
        pass3 = Events.RaidEvent(generate_raid({"move_1": 291}))
        # Test passing events
        for e in [pass1, pass2, pass3]:
            self.assertTrue(raid_filter.check_event(e))

        # Generate events that should fail
        fail1 = Events.RaidEvent(generate_raid({"move_1": 200}))
        fail2 = Events.RaidEvent(generate_raid({"move_1": 201}))
        fail3 = Events.RaidEvent(generate_raid({"move_1": 202}))

        # Test failing events
        for e in [fail1, fail2, fail3]:
            self.assertFalse(raid_filter.check_event(e))

    def test_charge_move(self):
        # Create the filters
        settings = {"charge_moves": [283, "14", "Solar Beam"]}
        raid_filter = Filters.RaidFilter('filter1', settings)

        # Generate events that should pass
        pass1 = Events.RaidEvent(generate_raid({"move_2": 283}))
        pass2 = Events.RaidEvent(generate_raid({"move_2": 14}))
        pass3 = Events.RaidEvent(generate_raid({"move_2": 116}))
        # Test passing events
        for e in [pass1, pass2, pass3]:
            self.assertTrue(raid_filter.check_event(e))

        # Generate events that should fail
        fail1 = Events.RaidEvent(generate_raid({"move_2": 200}))
        fail2 = Events.RaidEvent(generate_raid({"move_2": 201}))
        fail3 = Events.RaidEvent(generate_raid({"move_2": 202}))

        # Test failing events
        for e in [fail1, fail2, fail3]:
            self.assertFalse(raid_filter.check_event(e))

    def test_raid_lvl(self):
        # Create the filters
        settings = {"min_raid_lvl": 3, "max_raid_lvl": 5}
        raid_filter = Filters.RaidFilter('filter1', settings)

        # Generate events that should pass
        pass1 = Events.RaidEvent(generate_raid({"level": 3}))
        pass2 = Events.RaidEvent(generate_raid({"level": 4}))
        pass3 = Events.RaidEvent(generate_raid({"level": 5}))
        # Test passing events
        for e in [pass1, pass2, pass3]:
            self.assertTrue(raid_filter.check_event(e))

        # Generate events that should fail
        fail1 = Events.RaidEvent(generate_raid({"level": 1}))
        fail2 = Events.RaidEvent(generate_raid({"level": 2}))

        # Test failing events
        for e in [fail1, fail2]:
            self.assertFalse(raid_filter.check_event(e))

    def test_gym_names(self):
        # Create the filters
        settings = {"gym_name_matches": ["pass.\Z"]}
        raid_filter = Filters.RaidFilter('filter1', settings)

        # Generate events that should pass
        pass1 = Events.RaidEvent(generate_raid({"name": "pass1"}))
        pass2 = Events.RaidEvent(generate_raid({"name": "pass2"}))
        pass3 = Events.RaidEvent(generate_raid({"name": "pass3"}))
        # Test passing events
        for e in [pass1, pass2, pass3]:
            self.assertTrue(raid_filter.check_event(e))

        # Generate events that should fail
        fail1 = Events.RaidEvent(generate_raid({"name": "fail1"}))
        fail2 = Events.RaidEvent(generate_raid({"name": "failpass"}))
        fail3 = Events.RaidEvent(generate_raid({"name": "passfail"}))

        # Test failing events
        for e in [fail1, fail2, fail3]:
            self.assertFalse(raid_filter.check_event(e))

    def test_current_team(self):
        # Create the filters
        settings = {"current_teams": [1, "2", "Instinct"]}
        raid_filter = Filters.RaidFilter('filter1', settings)

        # Generate events that should pass
        pass1 = Events.RaidEvent(generate_raid({"team": 1}))
        pass2 = Events.RaidEvent(generate_raid({"team": 2}))
        pass3 = Events.RaidEvent(generate_raid({"team": 3}))
        # Test passing events
        for e in [pass1, pass2, pass3]:
            self.assertTrue(raid_filter.check_event(e))

        # Generate events that should fail
        fail1 = Events.RaidEvent(generate_raid({"team": 0}))

        # Test failing events
        for e in [fail1]:
            self.assertFalse(raid_filter.check_event(e))

# Create a generic raid, overriding with an specific values
def generate_raid(values):
    raid = {
        "gym_id": "OWNmOTFmMmM0YTY3NGQwYjg0Y2I1N2JlZjU4OWRkMTYuMTY=",
        "url": "???",
        "name": "unknown",
        "description": "???",
        "pokemon_id": 150,
        "cp": 12345,
        "move_1": 123,
        "move_2": 123,
        "start": 1499244052,
        "end": 1499246052,
        "level": 5,
        "latitude": 37.7876146,
        "longitude": -122.390624
    }
    raid.update(values)
    return raid

if __name__ == '__main__':
    unittest.main()

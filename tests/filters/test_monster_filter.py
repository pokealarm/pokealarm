import unittest
import PokeAlarm.Filters as Filters
import PokeAlarm.Events as Events


class TestMonsterFilter(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_monster_id(self):
        # Create the filters
        settings = {"monsters": [1, "2", "Venusaur"]}
        mon_filter = Filters.Monster('filter1', settings)

        # Generate events that should pass
        pass1 = Events.Monster(generate_generic_monster({"pokemon_id": 1}))
        pass2 = Events.Monster(generate_generic_monster({"pokemon_id": 2}))
        pass3 = Events.Monster(generate_generic_monster({"pokemon_id": 3}))
        # Test passing events
        for e in [pass1, pass2, pass3]:
            self.assertTrue(mon_filter.check_event(e))

        # Generate events that should fail
        fail1 = Events.Monster(generate_generic_monster({"pokemon_id": 5}))
        fail2 = Events.Monster(generate_generic_monster({"pokemon_id": 102}))
        fail3 = Events.Monster(generate_generic_monster({"pokemon_id": 30}))

        # Test failing events
        for e in [fail1, fail2, fail3]:
            self.assertFalse(mon_filter.check_event(e))

    def test_lvl(self):
        # Create the filters
        settings = {"min_lvl": 5, "max_lvl": 10}
        mon_filter = Filters.Monster('filter1', settings)

        # Generate events that should pass
        pass1 = Events.Monster(generate_generic_monster({"pokemon_level": 5}))
        pass2 = Events.Monster(generate_generic_monster({"pokemon_level": 7}))
        pass3 = Events.Monster(generate_generic_monster({"pokemon_level": 10}))
        # Test passing events
        for e in [pass1, pass2, pass3]:
            self.assertTrue(mon_filter.check_event(e))

        # Generate events that should fail
        fail1 = Events.Monster(generate_generic_monster({"pokemon_id": 4}))
        fail2 = Events.Monster(generate_generic_monster({"pokemon_id": 11}))
        fail3 = Events.Monster(generate_generic_monster({"pokemon_id": 100}))

        # Test failing events
        for e in [fail1, fail2, fail3]:
            self.assertFalse(mon_filter.check_event(e))


# Create a generic monster, overriding with an specific values
def generate_generic_monster(values):
    mon = {
        "encounter_id": "0",
        "spawnpoint_id": "0",
        "pokemon_id": 1,
        "pokemon_level": 1,
        "player_level": 40,
        "latitude": 37.7876146,
        "longitude": -122.390624,
        "disappear_time": 1506897031,
        "last_modified_time": 1475033386661,
        "time_until_hidden_ms": 5000,
        "seconds_until_despawn": 1754,
        "spawn_start": 2153,
        "spawn_end": 3264,
        "verified": False,
        "cp_multiplier": 0.7317000031471252,
        "form": None,
        "cp": None,
        "individual_attack": None,
        "individual_defense": None,
        "individual_stamina": None,
        "move_1": None,
        "move_2": None,
        "height": None,
        "weight": None,
        "gender": None
    }
    mon.update(values)
    return mon


if __name__ == '__main__':
    unittest.main()

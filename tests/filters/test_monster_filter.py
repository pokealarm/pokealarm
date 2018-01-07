import unittest
import sys
import PokeAlarm.Filters as Filters
import PokeAlarm.Events as Events

# ToDo: Find a better way
# Reinforce UTF-8 as default
reload(sys)
sys.setdefaultencoding('UTF8')


class TestMonsterFilter(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_monster_id(self):
        # Create the filters
        settings = {"monsters": [1, "2", "Venusaur"]}
        mon_filter = Filters.MonFilter('filter1', settings)

        # Generate events that should pass
        pass1 = Events.MonEvent(generate_monster({"pokemon_id": 1}))
        pass2 = Events.MonEvent(generate_monster({"pokemon_id": 2}))
        pass3 = Events.MonEvent(generate_monster({"pokemon_id": 3}))
        # Test passing events
        for e in [pass1, pass2, pass3]:
            self.assertTrue(mon_filter.check_event(e))

        # Generate events that should fail
        fail1 = Events.MonEvent(generate_monster({"pokemon_id": 5}))
        fail2 = Events.MonEvent(generate_monster({"pokemon_id": 102}))
        fail3 = Events.MonEvent(generate_monster({"pokemon_id": 30}))

        # Test failing events
        for e in [fail1, fail2, fail3]:
            self.assertFalse(mon_filter.check_event(e))

    def test_lvl(self):
        # Create the filters
        settings = {"min_lvl": 5, "max_lvl": 10}
        mon_filter = Filters.MonFilter('filter1', settings)

        # Generate events that should pass
        pass1 = Events.MonEvent(generate_monster({"pokemon_level": 5}))
        pass2 = Events.MonEvent(generate_monster({"pokemon_level": 7}))
        pass3 = Events.MonEvent(generate_monster({"pokemon_level": 10}))
        # Test passing events
        for e in [pass1, pass2, pass3]:
            self.assertTrue(mon_filter.check_event(e))

        # Generate events that should fail
        fail1 = Events.MonEvent(generate_monster({"pokemon_id": 4}))
        fail2 = Events.MonEvent(generate_monster({"pokemon_id": 11}))
        fail3 = Events.MonEvent(generate_monster({"pokemon_id": 100}))

        # Test failing events
        for e in [fail1, fail2, fail3]:
            self.assertFalse(mon_filter.check_event(e))

    def test_iv(self):
        # Create filter that forces settings
        settings = {"min_iv": 50, "max_iv": 75}
        mon_filter = Filters.MonFilter('iv_filter', settings)

        # Generate events that pass based off forced filter
        pass1 = create_event({  # test max
            "individual_attack": 15,
            "individual_defense": 15,
            "individual_stamina": 3
        })
        pass2 = create_event({  # in between
            "individual_attack": 15,
            "individual_defense": 10,
            "individual_stamina": 2
        })
        pass3 = create_event({  # test min
            "individual_attack": 10,
            "individual_defense": 8,
            "individual_stamina": 5
        })

        for e in [pass1, pass2, pass3]:
            self.assertTrue(mon_filter.check_event(e))

        # Generate events that fail based off the forced filter
        fail1 = create_event({  # test max
            "individual_attack": 12,
            "individual_defense": 11,
            "individual_stamina": 11
        })
        fail2 = create_event({  # Extreme end
            "individual_attack": 15,
            "individual_defense": 15,
            "individual_stamina": 15
        })
        fail3 = create_event({  # test min
            "individual_attack": 10,
            "individual_defense": 8,
            "individual_stamina": 4
        })

        for e in [fail1, fail2, fail3]:
            self.assertFalse(mon_filter.check_event(e))

    def test_attack(self):
        # Create filter that forces settings
        settings = {"min_atk": 5, "max_atk": 10}
        mon_filter = Filters.MonFilter('atk_filter', settings)

        # Generate events that pass based off forced filter
        pass1 = create_event({"individual_attack": 5})  # test min
        pass2 = create_event({"individual_attack": 7})  # test middle
        pass3 = create_event({"individual_attack": 10})  # test max

        for e in [pass1, pass2, pass3]:
            self.assertTrue(mon_filter.check_event(e))

        fail1 = create_event({"individual_attack": 4})  # test close to min
        fail2 = create_event({"individual_attack": 11})  # test close to max
        fail3 = create_event({"individual_attack": 1})  # test extreme

        for e in [fail1, fail2, fail3]:
            self.assertFalse(mon_filter.check_event(e))

    def test_defense(self):
        # Create filter that forces settings
        settings = {"min_def": 5, "max_def": 10}
        mon_filter = Filters.MonFilter('def_filter', settings)

        # Generate events that pass based off forced filter
        pass1 = create_event({"individual_defense": 5})  # test min
        pass2 = create_event({"individual_defense": 7})  # test middle
        pass3 = create_event({"individual_defense": 10})  # test max

        for e in [pass1, pass2, pass3]:
            self.assertTrue(mon_filter.check_event(e))

        fail1 = create_event({"individual_defense": 4})  # test close to min
        fail2 = create_event({"individual_defense": 11})  # test close to max
        fail3 = create_event({"individual_defense": 1})  # test extreme

        for e in [fail1, fail2, fail3]:
            self.assertFalse(mon_filter.check_event(e))

    def test_stamina(self):
        # Create filter that forces settings
        settings = {"min_sta": 5, "max_sta": 10}
        mon_filter = Filters.MonFilter('sta_filter', settings)

        # Generate events that pass based off forced filter
        pass1 = create_event({"individual_stamina": 5})  # test min
        pass2 = create_event({"individual_stamina": 7})  # test middle
        pass3 = create_event({"individual_stamina": 10})  # test max

        for e in [pass1, pass2, pass3]:
            self.assertTrue(mon_filter.check_event(e))

        fail1 = create_event({"individual_stamina": 4})  # test close to min
        fail2 = create_event({"individual_stamina": 11})  # test close to max
        fail3 = create_event({"individual_stamina": 1})  # test extreme

        for e in [fail1, fail2, fail3]:
            self.assertFalse(mon_filter.check_event(e))

    def test_form(self):
        # Create filter that forces settings
        settings = {"form_ids": [1, 28]}
        mon_filter = Filters.MonFilter('form_filter', settings)
        self.assertTrue(mon_filter.check_event(create_event({'form': 1})))
        self.assertTrue(mon_filter.check_event(create_event({'form': 28})))
        self.assertFalse(mon_filter.check_event(create_event({'form': 2})))
        self.assertFalse(mon_filter.check_event(create_event({'form': 999})))

    def test_moves(self):
        quick_settings = {"quick_moves": ["Vine Whip", "Tackle"]}
        quick_mon_filter = Filters.MonFilter('quick_move_filter',
                                             quick_settings)
        self.assertTrue(quick_mon_filter.check_event(create_event({
            'move_1': 221
        })))
        self.assertTrue(quick_mon_filter.check_event(create_event({
            'move_1': 214
        })))
        self.assertFalse(quick_mon_filter.check_event(create_event({
            'move_1': 1
        })))
        self.assertFalse(quick_mon_filter.check_event(create_event({
            'move_1': 999
        })))

        charge_settings = {"charge_moves": ["Sludge Bomb", "Seed Bomb"]}
        charge_mon_filter = Filters.MonFilter('charge_move_filter',
                                              charge_settings)
        self.assertTrue(charge_mon_filter.check_event(create_event({
            'move_2': 90
        })))
        self.assertTrue(charge_mon_filter.check_event(create_event({
            'move_2': 59
        })))
        self.assertFalse(charge_mon_filter.check_event(create_event({
            'move_2': 1
        })))
        self.assertFalse(charge_mon_filter.check_event(create_event({
            'move_2': 999
        })))

    def test_gender(self):
        settings = {'genders': ["male", "female"]}
        mon_filter = Filters.MonFilter('gender_filter', settings)
        self.assertTrue(mon_filter.check_event(create_event({'gender': 2})))
        self.assertFalse(mon_filter.check_event(create_event({'gender': 3})))

    def test_size(self):
        # Assumes base height/weight of Bulbasaur
        settings = {'sizes': ["tiny", "small", "large"]}
        mon_filter = Filters.MonFilter('size_filter', settings)
        self.assertTrue(mon_filter.check_event(create_event({
            'height': 0.71,
            'weight': 9
        })))
        self.assertFalse(mon_filter.check_event(create_event({
            'height': 0.71,
            'weight': 8
        })))

    def test_weight(self):
        settings = {'min_weight': 15, 'max_weight': 'inf'}
        mon_filter = Filters.MonFilter('weight_filter', settings)
        self.assertTrue(mon_filter.check_event(create_event({'weight': 15})))
        self.assertFalse(mon_filter.check_event(create_event({'weight': 14})))
        self.assertTrue(mon_filter.check_event(create_event({
            'weight': 'inf'
        })))

    def test_height(self):
        settings = {'min_height': 15, 'max_height': 'inf'}
        mon_filter = Filters.MonFilter('height_filter', settings)
        self.assertTrue(mon_filter.check_event(create_event({'height': 15})))
        self.assertFalse(mon_filter.check_event(create_event({'height': 14})))
        self.assertTrue(mon_filter.check_event(create_event({
            'height': 'inf'
        })))

    def test_distance(self):
        mon_event = Events.MonEvent(generate_monster({}))
        settings = {'min_dist': '5', 'max_dist': '2000'}
        mon_filter = Filters.MonFilter('distance_filter', settings)
        for i in [1000, 5, 2000]:
            mon_event.distance = i
            self.assertTrue(mon_filter.check_event(mon_event))

        settings2 = {'min_dist': '5', 'max_dist': 500}
        mon_filter2 = Filters.MonFilter('distance_filter_2', settings2)
        for i in [4, 501, 9999]:
            mon_event.distance = i
            self.assertFalse(mon_filter2.check_event(mon_event))

    def test_custom_dts(self):
        settings = {'custom_dts': {
            'key1': 'value1',
            'I\'m a goofy': 'goober yeah!'
        }}
        mon_filter = Filters.MonFilter('custom_dts_filter', settings)
        self.assertTrue(mon_filter.check_event(create_event({})))

    def test_missing_info(self):
        settings = {
            'is_missing_info': False,
            'min_atk': 5,
            'min_def': 5,
            'max_sta': 14
        }
        mon_filter = Filters.MonFilter('missing_info_filter', settings)
        self.assertTrue(mon_filter.check_event(create_event({
            'individual_attack': 15,
            'individual_defense': 15,
            'individual_stamina': 14,
            "cp": 280
        })))
        self.assertFalse(mon_filter.check_event(create_event({})))

    def test_cp(self):
        settings = {'min_cp': 20, 'max_cp': 500}
        mon_filter = Filters.MonFilter('cp_filter', settings)
        for i in [20, 250, 500]:
            self.assertTrue(mon_filter.check_event(create_event({'cp': i})))

        for i in [19, 501, 9999]:
            self.assertFalse(mon_filter.check_event(create_event({'cp': i})))


# Create a generic monster, overriding with an specific values
def generate_monster(values):
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


# Create the event and change default values
def create_event(items_to_change):
    return Events.MonEvent(generate_monster(items_to_change))


if __name__ == '__main__':
    unittest.main()

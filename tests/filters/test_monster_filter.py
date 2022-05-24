from datetime import datetime, timedelta
import time
import unittest
import PokeAlarm.Filters as Filters
import PokeAlarm.Events as Events
from PokeAlarm.Geofence import load_geofence_file
from tests.filters import MockManager, generic_filter_test, full_filter_test


class TestMonsterFilter(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls._mgr = MockManager()

    @classmethod
    def tearDown(cls):
        pass

    def gen_filter(self, settings):
        """ Generate a generic filter with given settings. """
        return Filters.MonFilter(self._mgr, "testfilter", settings)

    def gen_event(self, values):
        """ Generate a generic monster, overriding with an specific values. """
        settings = {
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
        settings.update(values)
        return Events.MonEvent(settings)

    @generic_filter_test
    def test_monster_id(self):
        self.filt = {"monsters": [1, "2", "Venusaur"]}
        self.event_key = "pokemon_id"
        self.pass_vals = [1, 2, 3]
        self.fail_vals = [5, 102, 30]

    @generic_filter_test
    def test_rarity(self):
        self.filt = {"rarity": ["new spawn", "Very Rare"]}
        self.event_key = "rarity"
        self.pass_vals = [0, 4]
        self.fail_vals = [1, 2, 5]

    @generic_filter_test
    def test_monsters_exclude(self):
        self.filt = {"monsters_exclude": [4, "5", "Charizard"]}
        self.event_key = "pokemon_id"
        self.pass_vals = [1, 2, 3]
        self.fail_vals = [4, 5, 6]

    @generic_filter_test
    def test_lvl(self):
        self.filt = {"min_lvl": 5, "max_lvl": 10}
        self.event_key = "pokemon_level"
        self.pass_vals = [5, 7, 10]
        self.fail_vals = [4, 11, 100]

    @generic_filter_test
    def test_shiny(self):
        self.filt = {"can_be_shiny": True}
        self.event_key = "pokemon_id"
        self.pass_vals = [1, 19, 152]
        self.fail_vals = [2, 5, 151]

    def test_iv(self):
        filt = self.gen_filter({"min_iv": 50, "max_iv": 75})

        pass_vals = [
            {
                "individual_attack": 15,
                "individual_defense": 15,
                "individual_stamina": 3
            },
            {
                "individual_attack": 15,
                "individual_defense": 10,
                "individual_stamina": 2
            },
            {
                "individual_attack": 10,
                "individual_defense": 8,
                "individual_stamina": 5
            }
        ]

        for val in pass_vals:
            event = self.gen_event(val)
            self.assertTrue(filt.check_event(event))

        fail_vals = [
            {
                "individual_attack": 12,
                "individual_defense": 11,
                "individual_stamina": 11
            },
            {
                "individual_attack": 15,
                "individual_defense": 15,
                "individual_stamina": 15
            },
            {
                "individual_attack": 10,
                "individual_defense": 8,
                "individual_stamina": 4
            }
        ]

        for val in fail_vals:
            event = self.gen_event(val)
            self.assertFalse(filt.check_event(event))

    @generic_filter_test
    def test_attack(self):
        self.filt = {"min_atk": 5, "max_atk": 10}
        self.event_key = "individual_attack"
        self.pass_vals = [5, 7, 10]
        self.fail_vals = [4, 11, 1]

    @generic_filter_test
    def test_defense(self):
        self.filt = {"min_def": 10, "max_def": 15}
        self.event_key = "individual_defense"
        self.pass_vals = [10, 12, 15]
        self.fail_vals = [4, 9, 16]

    @generic_filter_test
    def test_stamina(self):
        self.filt = {"min_sta": 3, "max_sta": 10}
        self.event_key = "individual_stamina"
        self.pass_vals = [3, 8, 10]
        self.fail_vals = [2, 11, 15]

    @generic_filter_test
    def test_form(self):
        self.filt = {"form_ids": [1, 28]}
        self.event_key = "form"
        self.pass_vals = [1, 28]
        self.fail_vals = [2, 999]

    @generic_filter_test
    def test_form_exclude(self):
        self.filt = {'exclude_forms': [1, 3, '55']}
        self.event_key = 'form'
        self.pass_vals = [2, 4, '111']
        self.fail_vals = [1, 3, '55']

    @generic_filter_test
    def test_costume(self):
        self.filt = {"costume_ids": [1, 2]}
        self.event_key = "costume"
        self.pass_vals = [1, 2]
        self.fail_vals = [3, 999]

    @generic_filter_test
    def test_costume_exclude(self):
        self.filt = {'exclude_costumes': ['123', 1, 2]}
        self.event_key = 'costume'
        self.pass_vals = [111, 3, '1234']
        self.fail_vals = [1, 2, '123']

    @generic_filter_test
    def test_quick_move(self):
        self.filt = {"quick_moves": ["Vine Whip", "Tackle"]}
        self.event_key = "move_1"
        self.pass_vals = [221, 214]
        self.fail_vals = [1, 999]

    @generic_filter_test
    def test_charge_move(self):
        self.filt = {"charge_moves": ["Sludge Bomb", "Seed Bomb"]}
        self.event_key = "move_2"
        self.pass_vals = [90, 59]
        self.fail_vals = [1, 999]

    @generic_filter_test
    def test_gender(self):
        self.filt = {'genders': ["male", "female"]}
        self.event_key = "gender"
        self.pass_vals = [1, 2]
        self.fail_vals = [3]

    def test_size(self):
        # Assumes base height/weight of Bulbasaur
        filt = self.gen_filter({'sizes': [1, "small", "4"]})
        # Test passing
        for val in [{'height': 0.71, 'weight': 9}]:
            event = self.gen_event(val)
            self.assertTrue(
                filt.check_event(event))
        # Test failing
        fails = [{'height': 0.71, 'weight': 8}, {'height': 0.71, 'weight': 8}]
        for val in fails:
            event = self.gen_event(val)
            self.assertFalse(filt.check_event(event))

    @generic_filter_test
    def test_weight(self):
        self.filt = {'min_weight': 15, 'max_weight': 25}
        self.event_key = 'weight'
        self.pass_vals = [15, 20, 25]
        self.fail_vals = [10, 14, 26, 100]

    @generic_filter_test
    def test_height(self):
        self.filt = {'min_height': 15, 'max_height': 25}
        self.event_key = 'height'
        self.pass_vals = [15, 20, 25]
        self.fail_vals = [10, 14, 26, 100]

    def test_mon_distance(self):
        # Create the filter
        filt = self.gen_filter(
            {"max_dist": 2000, "min_dist": 400})

        # Test passing
        mon = self.gen_event({})
        for dist in [1000, 800, 600]:
            mon.distance = dist
            self.assertTrue(filt.check_event(mon))

        # Test failing
        mon = self.gen_event({})
        for dist in [0, 300, 3000]:
            mon.distance = dist
            self.assertFalse(filt.check_event(mon))

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

    @generic_filter_test
    def test_cp(self):
        self.filt = {'min_cp': 20, 'max_cp': 500}
        self.event_key = "cp"
        self.pass_vals = [20, 250, 500]
        self.fail_vals = [19, 501, 9999]

    @generic_filter_test
    def test_weather(self):
        self.filt = {'weather': [1, "windy"]}
        self.event_key = "weather"
        self.pass_vals = [1, 5]
        self.fail_vals = [0, 2, 8]

    @generic_filter_test
    def test_boosted_weather(self):
        self.filt = {'boosted_weather': [1, 'windy']}
        self.event_key = 'boosted_weather'
        self.pass_vals = [1, 5]
        self.fail_vals = [0, 2, 8]

    @generic_filter_test
    def test_is_boosted_weather(self):
        self.filt = {'is_boosted_weather': True}
        self.event_key = 'boosted_weather'
        self.pass_vals = [1, 2, 5]
        self.fail_vals = [0]

    @generic_filter_test
    def test_types(self):
        self.filt = {'types': ["Dark"]}
        self.event_key = 'pokemon_id'
        self.pass_vals = [198, 261]
        self.fail_vals = [1, 4]

    def test_time_range(self):
        # Create a time filter with min_time and max_time set
        filt = self.gen_filter(
            {'min_time': "22:58", 'max_time': "0:25"})

        # Test passing
        for t in ["23:15", "22:58", "0:00", "0:25"]:
            filt._check_list[0].override_time(t)
            event = self.gen_event({"encounter_id": "1"})
            self.assertTrue(filt.check_event(event))

        # Test failing
        for t in ["22:57", "10:00", "20:50", "0:26"]:
            filt._check_list[0].override_time(t)
            event = self.gen_event({"encounter_id": "1"})
            self.assertFalse(filt.check_event(event))

        # Create a time filter with only min_time set
        filt = self.gen_filter(
            {'min_time': "22:58"})

        # Test passing
        for t in ["23:15", "22:58", "23:59"]:
            filt._check_list[0].override_time(t)
            event = self.gen_event({"encounter_id": "1"})
            self.assertTrue(filt.check_event(event))

        # Test failing
        for t in ["22:57", "10:00", "0:50", "0:00"]:
            filt._check_list[0].override_time(t)
            event = self.gen_event({"encounter_id": "1"})
            self.assertFalse(filt.check_event(event))

        # Create a time filter with only max_time set
        filt = self.gen_filter(
            {'max_time': "0:25"})

        # Test passing
        for t in ["0:00", "0:25"]:
            filt._check_list[0].override_time(t)
            event = self.gen_event({"encounter_id": "1"})
            self.assertTrue(filt.check_event(event))

        # Test failing
        for t in ["22:57", "10:00", "20:50", "0:26"]:
            filt._check_list[0].override_time(t)
            event = self.gen_event({"encounter_id": "1"})
            self.assertFalse(filt.check_event(event))

    def test_time_left(self):
        # Create the filter
        filt = self.gen_filter(
            {'min_time_left': 1000, 'max_time_left': 8000})

        # Test passing
        for s in [2000, 4000, 6000]:
            d = (datetime.now() + timedelta(seconds=s))
            t = time.mktime(d.timetuple())
            event = self.gen_event({"disappear_time": t})
            self.assertTrue(filt.check_event(event))

        # Test failing
        for s in [200, 999, 8001]:
            d = (datetime.now() + timedelta(seconds=s))
            t = time.mktime(d.timetuple())
            event = self.gen_event({"disappear_time": t})
            self.assertFalse(filt.check_event(event))

    def test_geofences(self):
        # Create the filter
        filt = self.gen_filter(
            {'geofences': ['NewYork']})

        geofences_ref = load_geofence_file("tests/filters/test_geofences.txt")
        filt._check_list[0].override_geofences_ref(geofences_ref)

        # Test passing
        for (lat, lng) in [(40.689256, -74.044510), (40.630720, -74.087673),
                           (40.686905, -73.853559)]:
            event = self.gen_event({"encounter_id": "1", "latitude": lat,
                                    "longitude": lng})
            self.assertTrue(filt.check_event(event))

        # Test failing
        for (lat, lng) in [(38.920936, -77.047371), (48.858093, 2.294694),
                           (-37.809022, 144.959003)]:
            event = self.gen_event({"encounter_id": "1", "latitude": lat,
                                    "longitude": lng})
            self.assertFalse(filt.check_event(event))

    def test_exclude_geofences(self):
        # Create the filter
        filt = self.gen_filter(
            {'exclude_geofences': ['NewYork']})

        geofences_ref = load_geofence_file("tests/filters/test_geofences.txt")
        filt._check_list[0].override_geofences_ref(geofences_ref)

        # Test passing
        for (lat, lng) in [(38.920936, -77.047371), (48.858093, 2.294694),
                           (-37.809022, 144.959003)]:
            event = self.gen_event({"latitude": lat,
                                    "longitude": lng})
            self.assertTrue(filt.check_event(event))

        # Test failing
        for (lat, lng) in [(40.689256, -74.044510), (40.630720, -74.087673),
                           (40.686905, -73.853559)]:
            event = self.gen_event({"latitude": lat,
                                    "longitude": lng})
            self.assertFalse(filt.check_event(event))

    @full_filter_test
    def test_pvp_min_max_great(self):
        self.filt = {'min_great': 56, 'max_great': 95}
        self.pass_items = [
            # 10 -> 11: 94.48% max stat
            {
                "pokemon_id": 10,
                "individual_attack": 15,
                "individual_defense": 15,
                "individual_stamina": 6
            },
            # 94.41% max stat
            {
                "pokemon_id": 15,
                "individual_attack": 0,
                "individual_defense": 0,
                "individual_stamina": 0
            },
            # 56.57% max stat
            {
                "pokemon_id": 235,
                "individual_attack": 0,
                "individual_defense": 0,
                "individual_stamina": 2
            }
        ]
        self.fail_items = [
            # 100% Max Stat
            {
                "pokemon_id": 227,
                "individual_attack": 0,
                "individual_defense": 15,
                "individual_stamina": 14
            },
            # 95.16% max stat
            {
                "pokemon_id": 15,
                "individual_attack": 0,
                "individual_defense": 2,
                "individual_stamina": 0
            },
            # 55.66% max stat
            {
                "pokemon_id": 235,
                "individual_attack": 0,
                "individual_defense": 0,
                "individual_stamina": 0
            }
        ]

    @full_filter_test
    def test_min_cp_great(self):
        self.filt = {'min_cp_great': 1000}
        self.pass_items = [
            # 1499 CP
            {
                'pokemon_id': 248,
                'individual_attack': 0,
                'individual_defense': 15,
                'individual_stamina': 15
            },
            # 1487 CP
            {
                'pokemon_id': 12,
                'individual_attack': 15,
                'individual_defense': 15,
                'individual_stamina': 15
            },
            # 1484 CP
            {
                'pokemon_id': 460,
                'individual_attack': 15,
                'individual_defense': 15,
                'individual_stamina': 15
            }
        ]
        self.fail_items = [
            # 431 CP
            {
                'pokemon_id': 235,
                'individual_attack': 15,
                'individual_defense': 15,
                'individual_stamina': 15
            }
        ]

    @full_filter_test
    def test_pvp_min_max_ultra(self):
        self.filt = {'min_ultra': 56, 'max_ultra': 95}
        self.pass_items = [
            # 10 -> 12: 94.36% max stat
            {
                "pokemon_id": 10,
                "individual_attack": 15,
                "individual_defense": 15,
                "individual_stamina": 5
            },
            # 75.16% max stat
            {
                "pokemon_id": 15,
                "individual_attack": 0,
                "individual_defense": 0,
                "individual_stamina": 0
            },
            # 56.57% max stat
            {
                "pokemon_id": 235,
                "individual_attack": 0,
                "individual_defense": 0,
                "individual_stamina": 2
            }
        ]
        self.fail_items = [
            # 100% Max Stat
            {
                "pokemon_id": 227,
                "individual_attack": 15,
                "individual_defense": 15,
                "individual_stamina": 15
            },
            # 95.11% max stat
            {
                "pokemon_id": 15,
                "individual_attack": 6,
                "individual_defense": 15,
                "individual_stamina": 15
            },
            # 55.66% max stat
            {
                "pokemon_id": 235,
                "individual_attack": 0,
                "individual_defense": 0,
                "individual_stamina": 0
            }
        ]

    @full_filter_test
    def test_min_cp_ultra(self):
        self.filt = {'min_cp_ultra': 2000}
        self.pass_items = [
            # 2465 CP
            {
                'pokemon_id': 248,
                'individual_attack': 0,
                'individual_defense': 0,
                'individual_stamina': 0
            },
            # 2471 CP
            {
                'pokemon_id': 130,
                'individual_attack': 15,
                'individual_defense': 15,
                'individual_stamina': 15
            },
            # 2465 CP
            {
                'pokemon_id': 473,
                'individual_attack': 0,
                'individual_defense': 15,
                'individual_stamina': 15
            }
        ]
        self.fail_items = [
            # 431 CP
            {
                'pokemon_id': 235,
                'individual_attack': 15,
                'individual_defense': 15,
                'individual_stamina': 15
            }
        ]


if __name__ == '__main__':
    unittest.main()

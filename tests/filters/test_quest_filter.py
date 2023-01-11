import unittest
import PokeAlarm.Filters as Filters
import PokeAlarm.Events as Events
from PokeAlarm.Geofence import load_geofence_file
from PokeAlarm.Utilities.QuestUtils import reward_string, get_quest_image
from PokeAlarm.Locale import Locale
from tests.filters import MockManager, generic_filter_test


class TestQuestFilter(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls._mgr = MockManager()

    @classmethod
    def tearDown(cls):
        pass

    def gen_filter(self, settings):
        """Generate a generic filter with given settings."""
        return Filters.QuestFilter(self._mgr, "testfilter", settings)

    def gen_event(self, values):
        """Generate a generic quest, overriding with an specific values."""
        settings = {
            "pokestop_id": 0,
            "name": "Stop Name",
            "url": "http://placehold.it/500x500",
            "latitude": 37.7876146,
            "longitude": -122.390624,
            "timestamp": 1506897031,
            "quest_reward_type": "Pokemon",
            "quest_reward_type_raw": 7,
            "quest_target": 0,
            "quest_type": "Catch 10 Dragonites",
            "quest_type_raw": 0,
            "item_type": "Pokemon",
            "item_amount": 1,
            "item_id": 0,
            "pokemon_id": 123,
            "pokemon_form": 0,
            "pokemon_costume": 0,
            "quest_task": "Catch 10 Dragonites",
            "quest_condition": "[]",
            "quest_template": "",
        }
        settings.update(values)
        return Events.QuestEvent(settings)

    def test_distance(self):
        # Create the filter
        filt = self.gen_filter({"max_dist": 2000, "min_dist": 400})

        # Test passing
        quest = self.gen_event({})
        for dist in [1000, 800, 600]:
            quest.distance = dist
            self.assertTrue(filt.check_event(quest))

        # Test failing
        quest = self.gen_event({})
        for dist in [0, 300, 3000]:
            quest.distance = dist
            self.assertFalse(filt.check_event(quest))

    @generic_filter_test
    def test_stop_name_contains(self):
        self.filt = {"stop_name_contains": ["stuff", "other", "uhh"]}
        self.event_key = "name"
        self.pass_vals = ["do stuff", "do other things", "uhh stewart"]
        self.fail_vals = ["you know", "I guess", "something"]

    @generic_filter_test
    def test_stop_name_excludes(self):
        self.filt = {"stop_name_excludes": ["stuff", "other", "uhh"]}
        self.event_key = "name"
        self.pass_vals = ["something", "else", "here"]
        self.fail_vals = ["some stuff", "some other", "uhh stewart"]

    @generic_filter_test
    def test_reward_types(self):
        self.filt = {"reward_types": [2, "Stardust", 7]}
        self.event_key = "quest_reward_type_raw"
        self.pass_vals = [2, 3, 7]
        self.fail_vals = [0, 1, 8, 111]

    @generic_filter_test
    def test_min_reward_amount(self):
        self.filt = {"min_reward_amount": 15}
        self.event_key = "item_amount"
        self.pass_vals = [15, 16, 111]
        self.fail_vals = [14, 0, -4]

    @generic_filter_test
    def test_max_reward_amount(self):
        self.filt = {"max_reward_amount": 20}
        self.event_key = "item_amount"
        self.pass_vals = [1, 19, 0]
        self.fail_vals = [21, 111, 123123]

    @generic_filter_test
    def test_monster_id(self):
        self.filt = {"monsters": [1, "2", "Venusaur"]}
        self.event_key = "pokemon_id"
        self.pass_vals = [1, 2, 3]
        self.fail_vals = [5, 102, 30]

    @generic_filter_test
    def test_monsters_exclude(self):
        self.filt = {"monsters_exclude": [4, "5", "Charizard"]}
        self.event_key = "pokemon_id"
        self.pass_vals = [1, 2, 3]
        self.fail_vals = [4, 5, 6]

    @generic_filter_test
    def test_form(self):
        self.filt = {"form_ids": [1, 28]}
        self.event_key = "pokemon_form"
        self.pass_vals = [1, 28]
        self.fail_vals = [2, 999]

    @generic_filter_test
    def test_costume(self):
        self.filt = {"costume_ids": [1, 2]}
        self.event_key = "pokemon_costume"
        self.pass_vals = [1, 2]
        self.fail_vals = [3, 999]

    @generic_filter_test
    def test_types(self):
        self.filt = {"types": ["Dark"]}
        self.event_key = "pokemon_id"
        self.pass_vals = [198, 261]
        self.fail_vals = [1, 4]

    @generic_filter_test
    def test_item_id(self):
        self.filt = {"items": ["Great Ball", "Max Revive", "Razz Berry", 501]}
        self.event_key = "item_id"
        self.pass_vals = [2, 202, 701, 501]
        self.fail_vals = [123, 0, -1, 999]

    @generic_filter_test
    def test_item_exclude(self):
        self.filt = {"items_exclude": ["Premier Ball", "101", 703]}
        self.event_key = "item_id"
        self.pass_vals = [1, 3, 555]
        self.fail_vals = [5, 101, 703]

    @generic_filter_test
    def test_template_contains(self):
        self.filt = {"template_contains": ["idk", "abc", "123"]}
        self.event_key = "quest_template"
        self.pass_vals = ["sssssidkss", "asdasdabcasd", "fjfjf123djdj"]
        self.fail_vals = ["something", "lets go", "play game"]

    @generic_filter_test
    def test_template_excludes(self):
        self.filt = {"template_excludes": ["aaa", "bbb", "ccc"]}
        self.event_key = "quest_template"
        self.pass_vals = ["asd", "bcd", "qwe"]
        self.fail_vals = ["123aaa123", "123bbb123", "123ccc123"]

    @generic_filter_test
    def test_task_contains(self):
        self.filt = {"task_contains": ["aaa", "bbb", "ccc"]}
        self.event_key = "quest_task"
        self.pass_vals = ["aaa", "bbb", "ccc"]
        self.fail_vals = ["eee", "fff", "ggg"]

    @generic_filter_test
    def test_task_excludes(self):
        self.filt = {"task_excludes": ["aaa", "bbb", "ccc"]}
        self.event_key = "quest_task"
        self.pass_vals = ["eee", "fff", "ggg"]
        self.fail_vals = ["aaa", "bbb", "ccc"]

    @generic_filter_test
    def test_shiny(self):
        self.filt = {"can_be_shiny": True}
        self.event_key = "pokemon_id"
        self.pass_vals = [1, 19, 193]
        self.fail_vals = [2, 5, 34]

    def test_reward_string(self):
        # Test monster reward
        quest = self.gen_event({"quest_reward_type_raw": 7, "item_amount": 1})
        reward = reward_string(quest, Locale("en"))
        self.assertIn("Scyther", reward)
        self.assertNotIn("Dragonite", reward)

        # Test item reward
        quest = self.gen_event(
            {"quest_reward_type_raw": 2, "item_amount": 3, "item_id": 2}
        )
        reward = reward_string(quest, Locale("en"))
        self.assertIn("Great Ball", reward)
        self.assertIn("3", reward)
        self.assertNotIn("Ultra Ball", reward)
        self.assertNotIn("4", reward)

        # Test stardust reward
        quest = self.gen_event({"quest_reward_type_raw": 3, "item_amount": 1000})
        reward = reward_string(quest, Locale("en"))
        self.assertIn("Stardust", reward)
        self.assertIn("1000", reward)
        self.assertNotIn("1001", reward)
        self.assertNotIn("Dusty dust", reward)

        # Test experience reward
        quest = self.gen_event({"quest_reward_type_raw": 1, "item_amount": 1000})
        reward = reward_string(quest, Locale("en"))
        self.assertIn("1000", reward)
        self.assertIn("Experience", reward)
        self.assertNotIn("1001", reward)
        self.assertNotIn("XP", reward)

    def test_image_name(self):
        # Test monster image
        quest = self.gen_event({"quest_reward_type_raw": 7, "item_amount": 1})
        image = get_quest_image(quest)
        self.assertIn("monsters/123_000", image)
        self.assertNotIn("124_000", image)

        # Test item reward
        quest = self.gen_event(
            {"quest_reward_type_raw": 2, "item_amount": 3, "item_id": 2}
        )
        image = get_quest_image(quest)
        self.assertIn("items/0002", image)
        self.assertNotIn("0003", image)

        # Test stardust reward
        quest = self.gen_event({"quest_reward_type_raw": 3, "item_amount": 1000})
        image = get_quest_image(quest)
        self.assertIn("quests/003", image)
        self.assertNotIn("004", image)

        # Test experience reward
        quest = self.gen_event({"quest_reward_type_raw": 1, "item_amount": 1000})
        image = get_quest_image(quest)
        self.assertIn("quests/001", image)
        self.assertNotIn("002", image)

    def test_geofences(self):
        # Create the filter
        filt = self.gen_filter({"geofences": ["NewYork"]})

        geofences_ref = load_geofence_file("tests/filters/test_geofences.txt")
        filt._check_list[0].override_geofences_ref(geofences_ref)

        # Test passing
        for (lat, lng) in [
            (40.689256, -74.044510),
            (40.630720, -74.087673),
            (40.686905, -73.853559),
        ]:
            event = self.gen_event({"latitude": lat, "longitude": lng})
            self.assertTrue(filt.check_event(event))

        # Test failing
        for (lat, lng) in [
            (38.920936, -77.047371),
            (48.858093, 2.294694),
            (-37.809022, 144.959003),
        ]:
            event = self.gen_event({"latitude": lat, "longitude": lng})
            self.assertFalse(filt.check_event(event))

    def test_exclude_geofences(self):
        # Create the filter
        filt = self.gen_filter({"exclude_geofences": ["NewYork"]})

        geofences_ref = load_geofence_file("tests/filters/test_geofences.txt")
        filt._check_list[0].override_geofences_ref(geofences_ref)

        # Test passing
        for (lat, lng) in [
            (38.920936, -77.047371),
            (48.858093, 2.294694),
            (-37.809022, 144.959003),
        ]:
            event = self.gen_event({"latitude": lat, "longitude": lng})
            self.assertTrue(filt.check_event(event))

        # Test failing
        for (lat, lng) in [
            (40.689256, -74.044510),
            (40.630720, -74.087673),
            (40.686905, -73.853559),
        ]:
            event = self.gen_event({"latitude": lat, "longitude": lng})
            self.assertFalse(filt.check_event(event))


if __name__ == "__main__":
    unittest.main()

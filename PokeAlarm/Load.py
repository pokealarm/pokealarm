# Standard Library Imports
import logging
import json
import traceback
import sys
from collections import OrderedDict
# 3rd Party Imports
# Local Import
import Utils as utils


log = logging.getLogger('LoadConfig')


def parse_rules_file(manager, filename):
    if str(filename).lower() == 'none':  # No Rules
        return
    filepath = utils.get_path(filename)
    rules = OrderedDict()
    try:
        log.info("Loading Rules from file at {}".format(filepath))
        with open(filepath, 'r') as f:
            rules = json.load(f, object_pairs_hook=OrderedDict)
        if type(rules) is not OrderedDict:
            log.critical("Rules files must be a JSON object:"
                         " { \"monsters\":[...],... }")
            raise ValueError("Rules file did not contain a dict.")
    except ValueError as e:
        log.error("Encountered error while loading Rules:"
                  " {}: {}".format(type(e).__name__, e))
        log.error(
            "PokeAlarm has encountered a 'ValueError' while loading the "
            "Rules file. This typically means the file isn't in the "
            "correct json format. Try loading the file contents into a "
            "json validator.")
        log.debug("Stack trace: \n {}".format(traceback.format_exc()))
        sys.exit(1)

    try:
        log.debug("Parsing 'monsters' section.")
        load_rules_section(manager.add_monster_rule, rules.pop('monsters', {}))
        log.debug("Parsing 'stops' section.")
        load_rules_section(manager.add_stop_rule, rules.pop('stops', {}))
        log.debug("Parsing 'gyms' section.")
        load_rules_section(manager.add_gym_rule, rules.pop('gyms', {}))
        log.debug("Parsing 'eggs' section.")
        load_rules_section(manager.add_egg_rule, rules.pop('eggs', {}))
        log.debug("Parsing 'raids' section.")
        load_rules_section(manager.add_raid_rule, rules.pop('raids', {}))
        log.debug("Parsing 'weather' section.")
        load_rules_section(manager.add_weather_rule, rules.pop('weather', {}))
        log.debug("Parsing 'quest' section.")
        load_rules_section(manager.add_quest_rule, rules.pop('quest', {}))

        for key in rules:
            raise ValueError("Unknown Event type '{}'. Rules must be defined "
                             "under the correct event type. See "
                             "example in rules.json.example.".format(key))

    except Exception as e:
        log.error("Encountered error while parsing Rules. "
                  "This is because of a mistake in your Rules file.")
        log.error("{}: {}".format(type(e).__name__, e))
        log.debug("Stack trace: \n {}".format(traceback.format_exc()))
        sys.exit(1)


def load_rules_section(set_rule, rules):
    for name, settings in rules.iteritems():
        if 'filters' not in settings:
            raise ValueError("{} rule is missing "
                             "a `filters` section.".format(name))
        if 'alarms' not in settings:
            raise ValueError("{} rule is missing "
                             "an `alarms` section.".format(name))

        filters = settings.pop('filters')
        alarms = settings.pop('alarms')
        set_rule(name, filters, alarms)

        if len(settings) > 0:
            raise ValueError("Rule {} has unknown parameters: {}".format(
                name, settings))

# Standard Library Imports
import logging
import json
import traceback
import sys
from collections import OrderedDict
# 3rd Party Imports
# Local Import
import Utils as utils
from Utils import require_and_remove_key, parse_boolean

log = logging.getLogger('pokealarm.setup')


def parse_filters_file(mgr, filename):
    try:
        filepath = utils.get_path(filename)
        log.info("Loading Filters from file at {}".format(filepath))
        with open(filepath, 'r') as f:
            filters_file = json.load(f, object_pairs_hook=OrderedDict)
        if type(filters_file) is not OrderedDict:
            log.critical("Filters files must be a JSON object:"
                         " { \"monsters\":{...},... }")
            raise ValueError("Filter file did not contain a dict.")
    except ValueError as e:
        log.error("Encountered error while loading Filters:"
                  " {}: {}".format(type(e).__name__, e))
        log.error(
            "PokeAlarm has encountered a 'ValueError' while loading the "
            "Filters file. This typically means the file isn't in the "
            "correct json format. Try loading the file contents into a "
            "json validator.")
        log.debug("Stack trace: \n {}".format(traceback.format_exc()))
        sys.exit(1)
    except IOError as e:
        log.error("Encountered error while loading Filters: "
                  "{}: {}".format(type(e).__name__, e))
        log.error("PokeAlarm was unable to find a filters file "
                  "at {}. Please check that this file exists "
                  "and that PA has read permissions.".format(filepath))
        log.debug("Stack trace: \n {}".format(traceback.format_exc()))
        sys.exit(1)

    try:
        # Load Monsters Section
        section = filters_file.pop('monsters', {'enabled': False})
        mgr.set_monsters_enabled(section.pop('enabled', True))
        filters = parse_filter_section(section)
        for name, f in filters.iteritems():
            mgr.add_monster_filter(name, f)

        # Load Stops Section
        section = filters_file.pop('stops', {'enabled': False})
        mgr.set_stops_enabled(section.pop('enabled', True))
        filters = parse_filter_section(section)
        for name, f in filters.iteritems():
            mgr.add_stop_filter(name, f)

        # Load Gyms Section
        section = filters_file.pop('gyms', {'enabled': False})
        mgr.set_gyms_enabled(section.pop('enabled', True))
        mgr.set_ignore_neutral(section.pop('ignore_neutral', True))
        filters = parse_filter_section(section)
        for name, f in filters.iteritems():
            mgr.add_gym_filter(name, f)

        # Load Eggs Section
        section = filters_file.pop('eggs', {'enabled': False})
        mgr.set_eggs_enabled(section.pop('enabled', True))
        filters = parse_filter_section(section)
        for name, f in filters.iteritems():
            mgr.add_egg_filter(name, f)

        # Load Raids Section
        section = filters_file.pop('raids', {'enabled': False})
        mgr.set_raids_enabled(section.pop('enabled', True))
        filters = parse_filter_section(section)
        for name, f in filters.iteritems():
            mgr.add_raid_filter(name, f)

        # Load Weather Section
        section = filters_file.pop('weather', {'enabled': False})
        mgr.set_weather_enabled(section.pop('enabled', True))
        filters = parse_filter_section(section)
        for name, f in filters.iteritems():
            mgr.add_weather_filter(name, f)

        return  # exit function

    except Exception as e:
        log.error("Encountered error while parsing Filters. "
                  "This is because of a mistake in your Filters file.")
        log.error("{}: {}".format(type(e).__name__, e))
        log.debug("Stack trace: \n {}".format(traceback.format_exc()))
        sys.exit(1)


def parse_filter_section(section):
    defaults = section.pop('defaults', {})
    default_dts = defaults.pop('custom_dts', {})
    filter_set = OrderedDict()
    for name, settings in section.pop('filters', {}).iteritems():
        settings = dict(defaults.items() + settings.items())
        local_dts = dict(default_dts.items()
                         + settings.pop('custom_dts', {}).items())
        if len(local_dts) > 0:
            settings['custom_dts'] = local_dts
        filter_set[name] = settings
    return filter_set


def parse_alarms_file(manager, filename):
    try:
        filepath = utils.get_path(filename)
        log.info("Loading Alarms from file at {}".format(filepath))
        with open(filepath, 'r') as f:
            alarm_settings = json.load(f, object_pairs_hook=OrderedDict)
        if type(alarm_settings) is not OrderedDict:
            log.critical("Alarms file must be an object of Alarms objects "
                         + "- { 'alarm1': {...}, ... 'alarm5': {...} }")
            sys.exit(1)
    except ValueError as e:
        log.error("Encountered error while loading Alarms:"
                  " {}: {}".format(type(e).__name__, e))
        log.error(
            "PokeAlarm has encountered a 'ValueError' while loading the "
            "Alarms file. This typically means the file isn't in the "
            "correct json format. Try loading the file contents into a "
            "json validator.")
        log.debug("Stack trace: \n {}".format(traceback.format_exc()))
        sys.exit(1)

    try:
        for name, alarm in alarm_settings.iteritems():
            active = parse_boolean(require_and_remove_key(
                'active', alarm, "Alarm objects in file."))
            if active:
                manager.add_alarm(name, alarm)
            else:
                log.debug("%s alarm ignored: active is set to 'false'", name)
    except Exception as e:
        log.error("Encountered error while loading Alarms: "
                  + "{}: {}".format(type(e).__name__, e))
        log.debug("Stack trace: \n {}".format(traceback.format_exc()))
        sys.exit(1)


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
            raise ValueError(
                "{} rule is missing a `filters` section.".format(name))
        if 'alarms' not in settings:
            raise ValueError(
                "{} rule is missing an `alarms` section.".format(name))

        filters = settings.pop('filters')
        alarms = settings.pop('alarms')
        set_rule(name, filters, alarms)

        if len(settings) > 0:
            raise ValueError(
                "Rule {} has unknown parameters: {}".format(name, settings))

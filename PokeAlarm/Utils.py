# -*- coding: utf-8 -*-
# Standard Library Imports
from datetime import datetime, timedelta
from glob import glob
import json
import logging
from math import radians, sin, cos, atan2, sqrt, degrees
import os
import sys
import hashlib
import hmac
import base64
import urllib.parse as urlparse
import traceback

# 3rd Party Imports
from s2cell import s2cell

# Local Imports
from PokeAlarm import not_so_secret_url
from PokeAlarm import config
from PokeAlarm import Unknown

log = logging.getLogger("Utils")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ SYSTEM UTILITIES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Checks is a line contains any substitutions located in args
def contains_arg(line, args):
    for word in args:
        if ("<" + word + ">") in line:
            return True
    return False


def get_path(path):
    if not os.path.isabs(path):  # If not absolute path
        path = os.path.join(config["ROOT_PATH"], path)
    return path


def parse_boolean(val):
    b = str(val).lower()
    if b in {"t", "true", "y", "yes"}:
        return True
    if b in ("f", "false", "n", "no"):
        return False
    return None


# Used for lazy installs - installs required module with pip
def pip_install(req, version):
    import subprocess

    target = "{}=={}".format(req, version)
    log.info("Attempting to pip install %s..." % target)
    subprocess.call(["pip", "install", target])
    log.info("%s install complete." % target)


# Used to exit when leftover parameters are found
def reject_leftover_parameters(dict_, location):
    if len(dict_) > 0:
        log.error("Unknown parameters at {}: ".format(location))
        log.error(list(dict_.keys()))
        log.error("Please consult the PokeAlarm wiki for accepted parameters.")
        sys.exit(1)


# Load a key from the given dict, or throw an error if it isn't there
def require_and_remove_key(key, _dict, location):
    if key in _dict:
        return _dict.pop(key)
    else:
        log.error(
            "The parameter '{}' is required for {}".format(key, location)
            + " Please check the PokeAlarm wiki for correct formatting."
        )
        sys.exit(1)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ POKEMON UTILITIES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# Returns the id corresponding with the pokemon name
# (use all locales for flexibility)
def get_pkmn_id(pokemon_name):
    try:
        name = pokemon_name.lower()
        return get_pkmn_id.ids.get(name)
    except AttributeError:
        get_pkmn_id.ids = {}
        files = glob(get_path("locales/*.json"))
        for file_ in files:
            with open(file_, "r") as f:
                j = json.load(f)
                f.close()
            j = j["pokemon"]
            for id_ in j:
                nm = j[id_].lower()
                get_pkmn_id.ids[nm] = int(id_)

        return get_pkmn_id.ids.get(name)


# Returns the id corresponding with the move (use all locales for flexibility)
def get_move_id(move_name):
    try:
        name = move_name.lower()
        return get_move_id.ids.get(name)
    except AttributeError:
        get_move_id.ids = {}
        files = glob(get_path("locales/*.json"))
        for file_ in files:
            with open(file_, "r") as f:
                j = json.load(f)
                f.close()
            j = j["moves"]
            for id_ in j:
                nm = j[id_].lower()
                get_move_id.ids[nm] = int(id_)

        return get_move_id.ids.get(name)


# Returns the id corresponding with the pokemon name
# (use all locales for flexibility)
def get_team_id(team_name):
    try:
        name = team_name.lower()
        return get_team_id.ids.get(name)
    except AttributeError:
        get_team_id.ids = {}
        files = glob(get_path("locales/*.json"))
        for file_ in files:
            with open(file_, "r") as f:
                j = json.load(f)
                f.close()
            j = j["teams"]
            for id_ in j:
                nm = j[id_].lower()
                get_team_id.ids[nm] = int(id_)

        return get_team_id.ids.get(name)


# Returns type id corresponding with the type name
def get_type_id(type_name):
    try:
        name = type_name.lower()
        return get_type_id.info.get(name, 0)
    except AttributeError:
        get_type_id.info = {}
        file_ = get_path("locales/en.json")
        with open(file_, "r") as f:
            j = json.load(f)
            f.close()
        for id_, name_ in j["types"].items():
            get_type_id.info[name_.lower()] = int(id_)

        return get_type_id.info.get(name, 0)


# Returns the types of a move when requesting
def get_move_type(move_id):
    try:
        return get_move_type.info.get(move_id, Unknown.SMALL)
    except AttributeError:
        get_move_type.info = {}
        file1_ = get_path("data/fast_moves.json")
        file2_ = get_path("data/charged_moves.json")
        for file_ in [file1_, file2_]:
            with open(file_, "r") as f:
                j = json.load(f)
                f.close()
            for mv in j:
                get_move_type.info[mv["move_id"]] = get_type_id(mv["type"])

        return get_move_type.info.get(move_id, Unknown.SMALL)


# Returns the damage of a move when requesting
def get_move_damage(move_id):
    try:
        return get_move_damage.info.get(move_id, "unkn")
    except AttributeError:
        get_move_damage.info = {}
        file1_ = get_path("data/fast_moves.json")
        file2_ = get_path("data/charged_moves.json")
        for file_ in [file1_, file2_]:
            with open(file_, "r") as f:
                j = json.load(f)
                f.close()
            for mv in j:
                get_move_damage.info[mv["move_id"]] = mv["power"]

        return get_move_damage.info.get(move_id, "unkn")


# Returns the dps of a move when requesting
def get_move_dps(move_id):
    try:
        return get_move_dps.info.get(move_id, "unkn")
    except AttributeError:
        get_move_dps.info = {}
        file1_ = get_path("data/fast_moves.json")
        file2_ = get_path("data/charged_moves.json")
        for file_ in [file1_, file2_]:
            with open(file_, "r") as f:
                j = json.load(f)
                f.close()
            for mv in j:
                get_move_dps.info[mv["move_id"]] = round(
                    (mv["power"] / mv["duration"]) * 1000, 2
                )

        return get_move_dps.info.get(move_id, "unkn")


# Returns the duration of a move when requesting
def get_move_duration(move_id):
    try:
        return get_move_duration.info.get(move_id, "unkn")
    except AttributeError:
        get_move_duration.info = {}
        file1_ = get_path("data/fast_moves.json")
        file2_ = get_path("data/charged_moves.json")
        for file_ in [file1_, file2_]:
            with open(file_, "r") as f:
                j = json.load(f)
                f.close()
            for mv in j:
                get_move_duration.info[mv["move_id"]] = mv["duration"]

        return get_move_duration.info.get(move_id, "unkn")


# Returns the duration of a move when requesting
def get_move_energy(move_id):
    try:
        return get_move_energy.info.get(move_id, "unkn")
    except AttributeError:
        get_move_energy.info = {}
        file1_ = get_path("data/fast_moves.json")
        file2_ = get_path("data/charged_moves.json")
        for file_ in [file1_, file2_]:
            with open(file_, "r") as f:
                j = json.load(f)
                f.close()
            for mv in j:
                get_move_energy.info[mv["move_id"]] = abs(mv["energy_delta"])

        return get_move_energy.info.get(move_id, "unkn")


# Returns the base height for a pokemon
def get_base_height(pokemon_id):
    try:
        return get_base_height.info.get(pokemon_id, 0)
    except AttributeError:
        get_base_height.info = {}
        file_ = get_path("data/pokemon_data.json")
        with open(file_, "r") as f:
            j = json.load(f)
            f.close()
        for id_ in j:
            get_base_height.info[int(id_)] = j[id_].get("height")

        return get_base_height.info.get(pokemon_id, 0)


# Returns the base weight for a pokemon
def get_base_weight(pokemon_id):
    try:
        return get_base_weight.info.get(pokemon_id, 0)
    except AttributeError:
        get_base_weight.info = {}
        file_ = get_path("data/pokemon_data.json")
        with open(file_, "r") as f:
            j = json.load(f)
            f.close()
        for id_ in j:
            get_base_weight.info[int(id_)] = j[id_].get("weight")

        return get_base_weight.info.get(pokemon_id, 0)


# Returns the types for a pokemon and its forms
def get_base_stats(pokemon_id, form_id=0):
    try:
        get_base_stats.info
    except AttributeError:
        get_base_stats.info = {}
        file_ = get_path("data/pokemon_data.json")
        with open(file_, "r") as f:
            j = json.load(f)
            f.close()
        for id_ in j:
            normal_form_stats = j[id_].get("stats")
            get_base_stats.info[int(id_) * 100_000] = normal_form_stats

            for form_id_ in j[id_].get("forms", {}):
                if form_id_ == "0":
                    continue
                form_ = j[id_]["forms"][form_id_]
                if (
                    form_["name"] in ("Shadow", "Purified", "Normal")
                    or form_.get("stats") is None
                ):
                    form_stats = normal_form_stats
                else:
                    form_stats = form_["stats"]
                stats_key = int(id_) * 100_000 + int(form_id_)
                get_base_stats.info[stats_key] = form_stats

    stats_key = pokemon_id * 100_000 + form_id
    default_stats = {"attack": 0, "defense": 0, "stamina": 0}
    return get_base_stats.info.get(stats_key, default_stats)


# Returns possible evolutions for a pokemon and its forms
def get_evolutions(base_pokemon_id, base_form_id=0):
    try:
        get_evolutions.info
    except AttributeError:
        get_evolutions.info = {}
        file_ = get_path("data/pokemon_data.json")
        with open(file_, "r") as f:
            j = json.load(f)
            f.close()
        for id_ in j:
            normal_form_chain = get_evolution_chain(j, id_, "0")
            get_evolutions.info[int(id_) * 100_000] = normal_form_chain
            for form_id_ in j[id_].get("forms", {}):
                if form_id_ == "0":
                    continue
                if j[id_]["forms"][form_id_]["name"] in (
                    "Shadow",
                    "Purified",
                    "Normal",
                ):
                    evo_chain = normal_form_chain
                else:
                    evo_chain = get_evolution_chain(j, id_, form_id_)

                evo_key = int(id_) * 100_000 + int(form_id_)
                get_evolutions.info[evo_key] = evo_chain

    evo_key = base_pokemon_id * 100_000 + base_form_id
    return get_evolutions.info.get(evo_key, [])


# Return the list of evolutions depending on the form of the pokemon
def get_evolution_chain(j, id_, form_id_, a=None):
    if a is None:
        a = []
    if form_id_ != "0":
        evolutions = j[id_]["forms"][form_id_].get("evolutions")
        if evolutions is not None:
            for evo_id in evolutions:
                if int(evo_id) > 905:  # block unreleased generations
                    continue

                evo_form_id = evolutions[evo_id]["form"]
                a.append((int(evo_id), int(evo_form_id)))

                next_id_ = str(evolutions[evo_id]["pokemon"])
                next_form_id_ = str(evolutions[evo_id]["form"])
                get_evolution_chain(j, next_id_, next_form_id_, a)
    else:
        evolutions = j[id_].get("evolutions")
        if evolutions is not None:
            for evo_id in evolutions:
                if int(evo_id) > 905:  # block unreleased generations
                    continue

                evo_form_id = evolutions[evo_id]["form"]
                a.append((int(evo_id), int(evo_form_id)))

                next_id_ = str(evolutions[evo_id]["pokemon"])
                get_evolution_chain(j, next_id_, "0", a)
    return a


# Returns evolution costs from a pokemon and its forms
def get_evolution_costs(pokemon_id, form_id=0):
    try:
        get_evolution_costs.info
    except AttributeError:
        get_evolution_costs.info = {}
        file_ = get_path("data/pokemon_data.json")
        with open(file_, "r") as f:
            j = json.load(f)
            f.close()
        for id_ in j:
            normal_form_chain = get_evolution_cost_chain(j, id_, "0")
            get_evolution_costs.info[int(id_) * 100_000] = normal_form_chain
            for form_id_ in j[id_].get("forms", {}):
                if form_id_ == "0":
                    continue
                if j[id_]["forms"][form_id_]["name"] in (
                    "Shadow",
                    "Purified",
                    "Normal",
                ):
                    cost_chain = normal_form_chain
                else:
                    cost_chain = get_evolution_cost_chain(j, id_, form_id_)

                mon_key = int(id_) * 100_000 + int(form_id_)
                get_evolution_costs.info[mon_key] = cost_chain

    mon_key = pokemon_id * 100_000 + form_id
    return get_evolution_costs.info.get(mon_key, [])


# Return the list of evolution costs depending on the form of the pokemon
def get_evolution_cost_chain(j, id_, form_id_, a=None):
    if a is None:
        a = []
    if form_id_ != "0":
        evolutions = j[id_]["forms"][form_id_].get("evolutions", {})
        for evo_id in evolutions:
            if int(evo_id) > 905:  # block unreleased generations
                continue

            candy_cost = int(evolutions[evo_id].get("candyCost", 0))
            a.append(candy_cost)

            get_evolution_cost_chain(
                j,
                str(evolutions[evo_id]["pokemon"]),
                str(evolutions[evo_id]["form"]),
                a,
            )
    else:
        evolutions = j[id_].get("evolutions", {})
        for evo_id in evolutions:
            if int(evo_id) > 905:  # block unreleased generations
                continue

            candy_cost = int(evolutions[evo_id].get("candyCost", 0))
            a.append(candy_cost)

            get_evolution_cost_chain(
                j,
                str(evolutions[evo_id]["pokemon"]),
                "0",
                a,
            )
    return a


# Returns default form names for all the pokemon
def get_raw_form_names():
    try:
        return get_raw_form_names.info
    except AttributeError:
        get_raw_form_names.info = {}
        file_ = get_path("data/pokemon_data.json")
        with open(file_, "r") as f:
            j = json.load(f)
            f.close()
        for id_ in j:
            get_raw_form_names.info[int(id_)] = {}
            get_raw_form_names.info[int(id_)][0] = "Normal"
            for form_id_ in j[id_].get("forms", {}):
                if form_id_ != "0":
                    get_raw_form_names.info[int(id_)][int(form_id_)] = j[id_]["forms"][
                        form_id_
                    ]["name"]

        return get_raw_form_names.info


# Return CP multipliers
def get_cp_multipliers():
    try:
        return get_cp_multipliers.info
    except AttributeError:
        file_ = get_path("data/cp_multipliers.json")
        with open(file_, "r") as f:
            j = json.load(f)
            get_cp_multipliers.info = {}
            for lvl in j:
                get_cp_multipliers.info[float(lvl)] = j[lvl]
        return get_cp_multipliers.info


def get_cp_multiplier_squares():
    try:
        return get_cp_multiplier_squares.info
    except AttributeError:
        multipliers = get_cp_multipliers()
        get_cp_multiplier_squares.info = {}
        for lvl in multipliers:
            get_cp_multiplier_squares.info[lvl] = multipliers[lvl] ** 2
        return get_cp_multiplier_squares.info


def bisect_levels(cp_limit, cp_base, first, last):
    try:
        bisect_levels.levels
    except AttributeError:
        # Generate levels tuple (1.0, 1.5, 2.0, ... , 49.5, 50.0)
        bisect_levels.levels = tuple(x / 10 for x in range(10, 501, 5))

    multiplier_squares = get_cp_multiplier_squares()

    best_cp = 0
    best_level = 0
    range_first = int(first * 2 - 2)
    range_last = int(last * 2 - 2)

    while range_first <= range_last:
        range_mid = (range_first + range_last) // 2
        level = bisect_levels.levels[range_mid]
        cp = max(10, int(cp_base * multiplier_squares[level]))

        if cp > cp_limit:
            range_last = range_mid - 1
        else:
            best_level = level
            best_cp = cp
            if cp < cp_limit:
                range_first = range_mid + 1
            else:
                break  # found exact limit

    return best_cp, best_level


# Get the max CP of a pokemon
def max_cp(monster_id, form_id=0):
    return calculate_cp(monster_id, form_id, 15, 15, 15, 50)


# Calculate CP using pokemon IV
def calculate_cp(monster_id, form_id, atk, de, sta, lvl):
    multipliers = get_cp_multiplier_squares()
    cp_base = calculate_cp_base(monster_id, form_id, atk, de, sta)
    return max(10, int(cp_base * multipliers[lvl]))


def calculate_cp_base(monster_id, form_id, atk, de, sta):
    base_stats = get_base_stats(monster_id, form_id)
    return (
        (base_stats["attack"] + atk)
        * sqrt(base_stats["defense"] + de)
        * sqrt(base_stats["stamina"] + sta)
        / 10
    )


def get_best_product(league, pokemon_id, form_id):
    try:
        get_best_product.info
    except AttributeError:
        get_best_product.info = {
            "great": {},
            "ultra": {},
        }
        file_ = get_path("data/stat_products.json")
        with open(file_, "r") as f:
            j = json.load(f)
            f.close()
        for id_ in j:
            for form_id_ in j[id_]:
                key_ = int(id_) * 100_000 + int(form_id_)
                get_best_product.info["great"][key_] = j[id_][form_id_].get(
                    "1500_highest_product"
                )
                get_best_product.info["ultra"][key_] = j[id_][form_id_].get(
                    "2500_highest_product"
                )

    base_key = pokemon_id * 100_000
    return get_best_product.info[league].get(
        base_key + form_id, get_best_product.info[league].get(base_key, 0)
    )


# Returns the highest possible stat product for PvP great league for a pkmn
def get_best_great_product(pokemon_id, form_id=0):
    return get_best_product("great", pokemon_id, form_id)


# Returns the highest possible stat product for PvP ultra league for a pkmn
def get_best_ultra_product(pokemon_id, form_id=0):
    return get_best_product("ultra", pokemon_id, form_id)


# Returns a cp range for a certain level of a pokemon caught in a raid
def get_pokemon_cp_range(level, pokemon_id, form_id=0):
    stats = get_base_stats(pokemon_id, form_id)

    try:
        cp_multi = get_pokemon_cp_range.info[level]
    except AttributeError:
        get_pokemon_cp_range.info = {}
        file_ = get_path("data/cp_multipliers.json")
        with open(file_, "r") as f:
            j = json.load(f)
            f.close()
        for lvl_ in j:
            get_pokemon_cp_range.info[float(lvl_)] = j[lvl_]

        cp_multi = get_pokemon_cp_range.info[level]

    # minimum IV for a egg/raid pokemon is 10/10/10
    min_cp = int(
        (
            (stats["attack"] + 10.0)
            * pow((stats["defense"] + 10.0), 0.5)
            * pow((stats["stamina"] + 10.0), 0.5)
            * pow(cp_multi, 2)
        )
        / 10.0
    )
    max_cp = int(
        (
            (stats["attack"] + 15.0)
            * pow((stats["defense"] + 15.0), 0.5)
            * pow((stats["stamina"] + 15.0), 0.5)
            * pow(cp_multi, 2)
        )
        / 10.0
    )

    return min_cp, max_cp


# Returns the size ratio of a pokemon
def size_ratio(pokemon_id, height, weight):
    height_ratio = height / get_base_height(pokemon_id)
    weight_ratio = weight / get_base_weight(pokemon_id)

    return height_ratio + weight_ratio


# Returns the appraised size_id of a pokemon
def get_pokemon_size(pokemon_id, height, weight):
    size = size_ratio(pokemon_id, height, weight)
    if size < 1.5:
        return 1
    elif size <= 1.75:
        return 2
    elif size <= 2.25:
        return 3
    elif size <= 2.5:
        return 4
    else:
        return 5


# Returns the gender symbol:
def get_gender_sym(gender):  # TODO - support other languages
    gender = str(gender).lower()
    if gender == "?":
        return "?"
    if gender == "1" or gender == "male":
        return "\u2642"  # male symbol
    elif gender == "2" or gender == "female":
        return "\u2640"  # female symbol
    elif gender == "3" or gender == "neutral":
        return "\u26b2"  # neutral
    else:
        raise ValueError(
            "Unable to interpret `{}` as a supported "
            " gender name or id.".format(gender)
        )


# Returns the types for a pokemon and its forms
def get_base_types(pokemon_id, form_id=0):
    try:
        get_base_types.info
    except AttributeError:
        get_base_types.info = {}
        file_ = get_path("data/pokemon_data.json")
        with open(file_, "r") as f:
            j = json.load(f)
            f.close()
        for id_ in j:
            normal_form_types = ([int(k) for k in j[id_].get("types")] + [0] * 2)[:2]
            get_base_types.info[int(id_) * 100_000] = normal_form_types

            for form_id_ in j[id_].get("forms", {}):
                if form_id_ == "0":
                    continue
                form_ = j[id_]["forms"][form_id_]
                if (
                    form_["name"] in ("Shadow", "Purified", "Normal")
                    or form_.get("types") is None
                ):
                    base_types = normal_form_types
                else:
                    base_types = ([int(k) for k in form_["types"]] + [0] * 2)[:2]

                mon_key = int(id_) * 100_000 + int(form_id_)
                get_base_types.info[mon_key] = base_types

    mon_key = pokemon_id * 100_000 + form_id
    return get_base_types.info.get(mon_key, [0, 0])


# Returns the types for a pokemon
def get_mon_type(pokemon_id, form_id=0):
    types = get_base_types(pokemon_id, form_id)
    return types["type1"], types["type2"]


def get_powerup_costs(type):
    try:
        return get_powerup_costs.info.get(type)
    except AttributeError:
        get_powerup_costs.info = {}
        file_ = get_path("data/powerup_costs.json")
        with open(file_, "r") as f:
            j = json.loads(f.read())
            f.close()
        for type_ in j:
            get_powerup_costs.info[type_] = []
            for key in j[type_]:
                levels = key.split("-")
                level = float(levels[0])
                endlevel = float(levels[1])
                while level <= endlevel:
                    get_powerup_costs.info[type_].append(int(j[type_][key]))
                    level += 0.5

        return get_powerup_costs.info.get(type)


# Return the list of stardust costs for powering up a pokemon
def get_stardust_costs():
    return get_powerup_costs("stardust")


# Return the list of candy costs for powering up a pokemon
def get_candy_costs():
    return get_powerup_costs("candy")


# Return the list of xl candy costs for powering up a pokemon
def get_xl_candy_costs():
    return get_powerup_costs("xl_candy")


def calculate_candy_cost(start_level, target_level, evo_candy_cost=0):
    if start_level >= target_level:
        return (0, 0)

    candy_costs = get_candy_costs()
    xl_candy_costs = get_xl_candy_costs()

    # Calculate indices from levels
    start = int(float(start_level) / 0.5 - 2)
    end = int(float(target_level) / 0.5 - 2)

    candy_cost = sum(candy_costs[start : min(80, end)], evo_candy_cost)
    xl_candy_cost = (
        sum(xl_candy_costs[0 : end - len(candy_costs)]) if target_level > 40 else 0
    )

    return (candy_cost, xl_candy_cost)


def calculate_stardust_cost(start_level, target_level):
    if start_level >= target_level:
        return 0

    stardust_costs = get_stardust_costs()

    # Calculate indices from levels
    start = int(float(start_level) / 0.5 - 2)
    end = int(float(target_level) / 0.5 - 2)

    return sum(stardust_costs[start:end])


def calculate_evolution_cost(monster_id, target_id, evolutions, evolution_costs):
    if monster_id == target_id or not ([True for s in evolutions if target_id == s[0]]):
        return 0
    evo_candy_cost = evolution_costs[0]

    for evo_id, evo_form_id in evolutions:
        if evo_id == target_id:
            return evo_candy_cost
        evo_candy_cost += evolution_costs[1]

    return evo_candy_cost


# Return a boolean for whether the monster or the type is weather boosted
def is_weather_boosted(weather_id, pokemon_id=0, form_id=0, mon_type=None):
    try:
        boosted_types = is_weather_boosted.info.get(str(weather_id), {})
    except AttributeError:
        is_weather_boosted.info = {}
        file_ = get_path("data/weather_boosts.json")
        with open(file_, "r") as f:
            j = json.load(f)
            f.close()
        for w_id in j:
            is_weather_boosted.info[w_id] = j[w_id]

        boosted_types = is_weather_boosted.info.get(str(weather_id), {})

    if mon_type is None:
        types = get_base_types(pokemon_id, form_id)
        return types[0] in boosted_types or types[1] in boosted_types
    else:
        return mon_type in boosted_types


def weather_id_is_boosted(desired_status, weather_id):
    if desired_status is True and weather_id != 0 and weather_id is not None:
        return True
    if desired_status is False and (weather_id == 0 or weather_id is None):
        return True
    return False


def get_weather_emoji(weather_id):
    return {
        1: "☀️",
        2: "☔️",
        3: "⛅",
        4: "☁️",
        5: "💨",
        6: "⛄️",
        7: "🌁",
    }.get(weather_id, "")


def get_type_emoji(type_id):
    return {
        1: "⭕",
        2: "🥋",
        3: "🐦",
        4: "☠",
        5: "⛰️",
        6: "💎",
        7: "🐛",
        8: "👻",
        9: "⚙",
        10: "🔥",
        11: "💧",
        12: "🍃",
        13: "⚡",
        14: "🔮",
        15: "❄",
        16: "🐲",
        17: "🌑",
        18: "💫",
    }.get(type_id, "")


def get_spawn_verified_emoji(spawn_verified_id):
    return {
        0: "❌",
        1: "✅",
    }.get(spawn_verified_id, "❔")


def get_team_emoji(team_id):
    return {
        0: "⚪",
        1: "🔵",
        2: "🔴",
        3: "🟡",
    }.get(team_id, "❔")


def get_ex_eligible_emoji(ex_eligible):
    return {
        0: "",
        1: "✉️",
    }.get(ex_eligible, "")


def get_shiny_emoji(can_be_shiny):
    if can_be_shiny:
        return "✨"
    else:
        return ""


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ MAPS API UTILITIES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# Returns a String link to Google Maps Pin at the location
def get_gmaps_link(lat, lng, nav=False):
    _api = "dir" if nav else "search"
    _prm = "destination" if nav else "query"
    latlng = f"{lat:5f}%2C{lng:5f}"
    return f"https://www.google.com/maps/{_api}/?api=1&{_prm}={latlng}"


# Returns a String link to Apple Maps Pin at the location
def get_applemaps_link(lat, lng, nav=False):
    _prm = "daddr" if nav else "address"
    latlng = f"{lat:5f}%2C{lng:5f}"
    return f"https://maps.apple.com/maps?{_prm}={latlng}&t=m"


# Returns a String link to Waze Maps Navigation at the location
def get_waze_link(lat, lng, nav=False):
    _nav = "yes" if nav else "no"
    latlng = f"{lat:5f}%2C{lng:5f}"
    return f"https://waze.com/ul?navigate={_nav}&ll={latlng}"


# Returns a static map url with <lat> and <lng> parameters for dynamic test
def get_gmaps_static_url(settings, api_key=None):
    if api_key is None or not parse_boolean(settings.get("enabled", "True")):
        return None
    width = settings.get("width", "250")
    height = settings.get("height", "125")
    maptype = settings.get("maptype", "roadmap")
    zoom = settings.get("zoom", "15")

    center = "<lat>%2C<lng>"
    query_center = f"center={center}"
    query_markers = f"markers=color:red%7C{center}"
    query_size = f"size={width}x{height}"
    query_zoom = f"zoom={zoom}"
    query_maptype = f"maptype={maptype}"
    query_key = f"key={api_key}"

    map_ = (
        "https://www.google.com/maps/api/staticmap?maptype=roadmap"
        f"{query_center}&{query_markers}&{query_maptype}&"
        f"{query_size}&{query_zoom}&{query_key}"
    )

    return map_


# Signs the Static Map URL using a URL signing secret
def sign_gmaps_static_url(input_url=None, secret=None):
    if input_url is None:
        log.error("Maps static url is required is to sign it")

    # If there is no signing secret, return the unsigned url
    if secret is None:
        log.debug("Signing secret is not defined. Using unsigned url.")
        return input_url

    try:
        url = urlparse.urlparse(input_url)

        # We only need to sign the path+query part of the string
        url_to_sign = f"{url.path}?{url.query}"

        # Decode the private key into its binary format
        # We need to decode the URL-encoded private key
        decoded_key = base64.urlsafe_b64decode(secret)

        # Create a signature using the private key and the URL-encoded
        # string using HMAC SHA1. This signature will be binary.
        signature = hmac.new(decoded_key, str.encode(url_to_sign), hashlib.sha1)

        # Encode the binary signature into base64 for use within a URL
        encoded_signature = base64.urlsafe_b64encode(signature.digest())

        original_url = f"{url.scheme}://{url.netloc}{url.path}?{url.query}"

        # Return signed URL
        return f"{original_url}&signature={encoded_signature.decode()}"

    except Exception as e:
        log.error(f"Unable to sign maps static url: {e}. Using unsigned url.")
        log.debug("Stack trace: \n {}".format(traceback.format_exc()))

        return input_url


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ GENERAL UTILITIES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


# Returns a cardinal direction (N/NW/W/SW, etc)
# of the pokemon from the origin point, if set
def get_cardinal_dir(pt_a, pt_b=None):
    if pt_b is None:
        return "?"

    lat1, lng1, lat2, lng2 = map(radians, [pt_b[0], pt_b[1], pt_a[0], pt_a[1]])
    directions = ["S", "SE", "E", "NE", "N", "NW", "W", "SW", "S"]
    bearing = (
        degrees(
            atan2(
                cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(lng2 - lng1),
                sin(lng2 - lng1) * cos(lat2),
            )
        )
        + 450
    ) % 360
    return directions[int(round(bearing / 45))]


# Return the distance formatted correctly
def get_dist_as_str(dist, units):
    if units == "imperial":
        if dist > 1760:  # yards per mile
            return "{:.1f}mi".format(dist / 1760.0)
        else:
            return "{:.1f}yd".format(dist)
    else:  # Metric
        if dist > 1000:  # meters per km
            return "{:.1f}km".format(dist / 1000.0)
        else:
            return "{:.1f}m".format(dist)


# Returns an integer representing the distance between A and B
def get_earth_dist(pt_a, pt_b=None, units="imperial"):
    if type(pt_a) is str or pt_b is None:
        return "unkn"  # No location set
    lat_a = radians(pt_a[0])
    lng_a = radians(pt_a[1])
    lat_b = radians(pt_b[0])
    lng_b = radians(pt_b[1])
    lat_delta = lat_b - lat_a
    lng_delta = lng_b - lng_a
    a = sin(lat_delta / 2) ** 2 + cos(lat_a) * cos(lat_b) * sin(lng_delta / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    radius = 6373000  # radius of earth in meters
    if units == "imperial":
        radius = 6975175  # radius of earth in yards
    dist = c * radius
    return dist


# Return the time as a string in different formats
def get_time_as_str(t, timezone=None):
    if timezone is None:
        timezone = config.get("TIMEZONE")
    s = (t - datetime.utcnow()).total_seconds()
    (m, s) = divmod(s, 60)
    (h, m) = divmod(m, 60)
    d = timedelta(hours=h, minutes=m, seconds=s)
    if timezone is not None:
        disappear_time = datetime.now(tz=timezone) + d
    else:
        disappear_time = datetime.now() + d
    # Time remaining in minutes and seconds
    time = "%dm %ds" % (m, s) if h == 0 else "%dh %dm" % (h, m)
    # Disappear time in 12h format, eg "2:30:16 PM"
    time_12h = (
        disappear_time.strftime("%I:%M:%S") + disappear_time.strftime("%p").lower()
    )
    # Disappear time in 24h format including seconds, eg "14:30:16"
    time_24h = disappear_time.strftime("%H:%M:%S")

    # Get the same as above but without seconds
    time_no_sec = "%dm" % m if h == 0 else "%dh %dm" % (h, m)
    time_12h_no_sec = (
        disappear_time.strftime("%I:%M") + disappear_time.strftime("%p").lower()
    )
    time_24h_no_sec = disappear_time.strftime("%H:%M")

    time_raw_hours = int(h)
    time_raw_minutes = int(m)
    time_raw_seconds = int(s)

    return (
        time,
        time_12h,
        time_24h,
        time_no_sec,
        time_12h_no_sec,
        time_24h_no_sec,
        time_raw_hours,
        time_raw_minutes,
        time_raw_seconds,
    )


# Return the time in seconds
def get_seconds_remaining(t, timezone=None):
    if timezone is None:
        timezone = config.get("TIMEZONE")
    seconds = (t - datetime.utcnow()).total_seconds()
    return seconds


# Return the default url for images and stuff
def get_image_url(suffix):
    return not_so_secret_url + suffix


# Returns the id corresponding with the weather
# (use all locales for flexibility)
def get_weather_id(weather_name):
    try:
        name = str(weather_name).lower()
        id_found = name in get_weather_id.ids
    except AttributeError:
        get_weather_id.ids = {}
        files = glob(get_path("locales/*.json"))
        for file_ in files:
            with open(file_, "r") as f:
                j = json.load(f)
                f.close()
            j = j["weather"]
            for id_ in j:
                nm = j[id_].lower()
                get_weather_id.ids[nm] = int(id_)

        id_found = name in get_weather_id.ids

    try:
        if id_found:
            return get_weather_id.ids[name]
        else:
            return int(name)  # try as an integer
    except ValueError:
        raise ValueError(
            f"Unable to interpret `{weather_name}` as a valid weather name or id."
        )


# Returns the id of the cached weather from (lat,lng)
def get_cached_weather_id_from_coord(lat, lng, cache):
    cell_id = s2cell.lat_lon_to_cell_id(lat, lng, 10)
    return cache.cell_weather_id(str(cell_id))


# Returns true if any item is in the provided list
def match_items_in_array(list, items):
    for obj in list:
        if obj in items:
            return True
    return False


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

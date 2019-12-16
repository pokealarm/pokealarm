import json
import os
from math import sqrt
from PokeAlarm import config
import PokeAlarm.Utils as utils
import logging

log = logging.getLogger('PvpUtils')


def get_path(path):
    if not os.path.isabs(path):  # If not absolute path
        path = os.path.join(config['ROOT_PATH'], path)
    return path


def mon(number):
    number = str(number)
    if len(number) == 1:
        number = "00" + number
    elif len(number) == 2:
        number = "0" + number
    elif len(number) != 3:
        raise ValueError
    return str(number)


def calculate_cp(mon, atk, de, sta, lvl):
    base_stats = utils.get_base_stats(int(mon))
    lvl = str(lvl).replace(".0", "")
    cp = ((base_stats["attack"] + atk) * sqrt(base_stats["defense"] + de) *
          sqrt(base_stats["stamina"] + sta) * (multipliers[str(lvl)]**2)
          / 10)
    return int(cp)


def max_cp(mon):
    cp = calculate_cp(mon, 15, 15, 15, 40)
    return int(cp)


def pokemon_rating(limit, mon, atk, de, sta, min_level, max_level):
    base_stats = utils.get_base_stats(int(mon))
    highest_rating = 0
    highest_cp = 0
    highest_level = 0
    for level in range(int(min_level * 2), int((max_level + 0.5) * 2)):
        level = str(level / float(2)).replace(".0", "")
        cp = calculate_cp(mon, atk, de, sta, level)
        if not cp > limit:
            attack = ((base_stats["attack"] + atk) * (multipliers[str(level)]))
            defense = ((base_stats["defense"] + de) *
                        (multipliers[str(level)]))
            stamina = int(((base_stats["stamina"] + sta) *
                             (multipliers[str(level)])))
            product = (attack * defense * stamina)
            if product > highest_rating:
                highest_rating = product
                highest_cp = cp
                highest_level = level
    return highest_rating, highest_cp, highest_level


def max_level(limit, pokemon):
    if not max_cp(mon(pokemon)) > limit:
        return float(40)
    for x in range(80, 2, -1):
        x = (x * 0.5)
        if calculate_cp(mon(pokemon), 0, 0, 0, x) <= limit:
            return min(x + 1, 40)


def min_level(limit, pokemon):
    if not max_cp(mon(pokemon)) > limit:
        return float(40)
    for x in range(80, 2, -1):
        x = (x * 0.5)
        if calculate_cp(mon(pokemon), 15, 15, 15, x) <= limit:
            return max(x - 1, 1)


def get_pvp_info(pokemon, atk, de, sta, lvl):
    global multipliers

    pokemon = mon(pokemon)
    lvl = float(lvl)
    multipliers = utils.get_cp_multipliers()
    stats_great_product = utils.get_great_product(int(pokemon))
    stats_ultra_product = utils.get_ultra_product(int(pokemon))
    evolutions = utils.get_evolutions(int(pokemon))

    great_product, great_cp, great_level = pokemon_rating(1500, pokemon, atk,
            de, sta, min_level(1500, pokemon), max_level(1500, pokemon))
    great_rating = 100 * (great_product / stats_great_product)
    ultra_product, ultra_cp, ultra_level = pokemon_rating(2500, pokemon, atk,
            de, sta, min_level(2500, pokemon), max_level(2500, pokemon))
    ultra_rating = 100 * (ultra_product / stats_ultra_product)
    great_id = int(pokemon)
    ultra_id = int(pokemon)

    if float(great_level) < lvl:
        great_rating = 0
    if float(ultra_level) < lvl:
        ultra_rating = 0

    for evo in evolutions:
        pokemon = mon(evo)
        stats_great_product = utils.get_great_product(int(pokemon))
        stats_ultra_product = utils.get_ultra_product(int(pokemon))

        great_product, evo_great_cp, evo_great_level = pokemon_rating(1500,
            pokemon, atk, de, sta, min_level(1500, pokemon),
            max_level(1500, pokemon))
        ultra_product, evo_ultra_cp, evo_ultra_level = pokemon_rating(2500,
                pokemon, atk, de, sta, min_level(2500, pokemon),
                max_level(2500, pokemon))
        evogreat = 100 * (great_product / stats_great_product)
        evoultra = 100 * (ultra_product / stats_ultra_product)

        if float(evo_great_level) < lvl:
            evogreat = 0
        if float(evo_ultra_level) < lvl:
            evoultra = 0

        if evogreat > great_rating:
            great_rating = evogreat
            great_cp = evo_great_cp
            great_level = evo_great_level
            great_id = int(pokemon)

        if evoultra > ultra_rating:
            ultra_rating = evoultra
            ultra_cp = evo_ultra_cp
            ultra_level = evo_ultra_level
            ultra_id = int(pokemon)

    return (float("{0:.2f}".format(great_rating)), great_id, great_cp,
            great_level, float("{0:.2f}".format(ultra_rating)), ultra_id,
            ultra_cp, ultra_level)

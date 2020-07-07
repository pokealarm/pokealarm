from math import sqrt
import PokeAlarm.Utils as utils
import logging

log = logging.getLogger('PvpUtils')


def calculate_cp(monster, atk, de, sta, lvl):
    multipliers = utils.get_cp_multipliers()
    base_stats = utils.get_base_stats(int(monster))
    lvl = str(lvl).replace(".0", "")
    cp = ((base_stats["attack"] + atk) * sqrt(base_stats["defense"] + de) *
          sqrt(base_stats["stamina"] + sta) * (multipliers[str(lvl)]**2)
          / 10)
    return int(cp)


def max_cp(monster):
    return calculate_cp(monster, 15, 15, 15, 40)


def pokemon_rating(limit, monster, atk, de, sta, min_level, max_level):
    multipliers = utils.get_cp_multipliers()
    base_stats = utils.get_base_stats(int(monster))
    highest_rating = 0
    highest_cp = 0
    highest_level = 0
    for level in range(int(min_level * 2), int((max_level + 0.5) * 2)):
        level = str(level / float(2)).replace(".0", "")
        cp = calculate_cp(monster, atk, de, sta, level)
        if not cp > limit:
            attack = (base_stats["attack"] + atk) * multipliers[str(level)]
            defense = (base_stats["defense"] + de) * multipliers[str(level)]
            stamina = int(((base_stats["stamina"] + sta) *
                           (multipliers[str(level)])))
            product = attack * defense * stamina
            if product > highest_rating:
                highest_rating = product
                highest_cp = cp
                highest_level = level
    return highest_rating, highest_cp, highest_level


def max_level(limit, monster):
    if not max_cp(monster) > limit:
        return float(40)
    for x in range(80, 2, -1):
        x = (x * 0.5)
        if calculate_cp(monster, 0, 0, 0, x) <= limit:
            return min(x + 1, 40)


def min_level(limit, monster):
    if not max_cp(monster) > limit:
        return float(40)
    for x in range(80, 2, -1):
        x = (x * 0.5)
        if calculate_cp(monster, 15, 15, 15, x) <= limit:
            return max(x - 1, 1)


def get_pvp_info(monster_id, atk, de, sta, lvl):
    monster = '{:03}'.format(monster_id)

    lvl = float(lvl)
    stats_great_product = utils.get_great_product(monster_id)
    stats_ultra_product = utils.get_ultra_product(monster_id)
    evolutions = utils.get_evolutions(monster_id)

    great_product, great_cp, great_level = pokemon_rating(
        1500, monster, atk, de, sta, min_level(1500, monster),
        max_level(1500, monster))
    great_rating = 100 * (great_product / stats_great_product)
    ultra_product, ultra_cp, ultra_level = pokemon_rating(
        2500, monster, atk, de, sta, min_level(2500, monster),
        max_level(2500, monster))
    ultra_rating = 100 * (ultra_product / stats_ultra_product)
    great_id = monster_id
    ultra_id = monster_id

    if float(great_level) < lvl:
        great_rating = 0
    if float(ultra_level) < lvl:
        ultra_rating = 0

    for evolution in evolutions:
        evolution_id = int(evolution)
        stats_great_product = utils.get_great_product(evolution_id)
        stats_ultra_product = utils.get_ultra_product(evolution_id)

        great_product, evo_great_cp, evo_great_level = pokemon_rating(
            1500, evolution, atk, de, sta, min_level(1500, evolution),
            max_level(1500, evolution))
        ultra_product, evo_ultra_cp, evo_ultra_level = pokemon_rating(
            2500, evolution, atk, de, sta, min_level(2500, evolution),
            max_level(2500, evolution))
        evo_great = 100 * (great_product / stats_great_product)
        evo_ultra = 100 * (ultra_product / stats_ultra_product)

        if float(evo_great_level) < lvl:
            evo_great = 0
        if float(evo_ultra_level) < lvl:
            evo_ultra = 0

        if evo_great > great_rating:
            great_rating = evo_great
            great_cp = evo_great_cp
            great_level = evo_great_level
            great_id = evolution_id

        if evo_ultra > ultra_rating:
            ultra_rating = evo_ultra
            ultra_cp = evo_ultra_cp
            ultra_level = evo_ultra_level
            ultra_id = evolution_id

    return (float("{0:.2f}".format(great_rating)), great_id, great_cp,
            great_level, float("{0:.2f}".format(ultra_rating)), ultra_id,
            ultra_cp, ultra_level)

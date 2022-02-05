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
    return calculate_cp(monster, 15, 15, 15, 50)


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
        return float(50)
    for x in range(100, 2, -1):
        x = (x * 0.5)
        if calculate_cp(monster, 0, 0, 0, x) <= limit:
            return min(x + 1, 50)


def min_level(limit, monster):
    if not max_cp(monster) > limit:
        return float(50)
    for x in range(100, 2, -1):
        x = (x * 0.5)
        if calculate_cp(monster, 15, 15, 15, x) <= limit:
            return max(x - 1, 1)


def calculate_candy_cost(start_level, target_level, evo_candy_cost=0):
    start_level = float(start_level)
    target_level = float(target_level)
    candy_table = [1] * 20 + [2] * 20 + [3] * 10 + [4] * 10 + \
        [6] * 4 + [8] * 4 + [10] * 4 + [12] * 4 + [15] * 2
    xl_candy_table = [10, 12, 15, 17, 20]
    tmp_level = start_level
    candy_cost = evo_candy_cost
    xl_candy_cost = 0

    while tmp_level != target_level and tmp_level < 40:
        tmp_level += 0.5
        cost_id = int((tmp_level - 1.5) / 0.5)
        candy_cost += candy_table[cost_id]

    while tmp_level != target_level:
        tmp_level += 0.5
        cost_id = int((tmp_level - 40.5) // 2)
        xl_candy_cost += xl_candy_table[cost_id]

    if xl_candy_cost != 0:
        return f'{candy_cost:,} + {xl_candy_cost:,} XL'.replace(',', ' ')
    else:
        return f'{candy_cost:,}'.replace(',', ' ')


def calculate_stardust_cost(start_level, target_level):
    start_level = float(start_level)
    target_level = float(target_level)
    stardust_table = [200, 400, 600, 800, 1000, 1300, 1600, 1900, 2200,
                      2500, 3000, 3500, 4000, 4500, 5000, 6000, 7000,
                      8000, 9000, 10000, 11000, 12000, 13000, 14000, 15000]

    tmp_level = start_level
    stardust_cost = 0
    while tmp_level != target_level:
        tmp_level += 0.5
        cost_id = int(tmp_level - 1.5) // 2
        stardust_cost += stardust_table[cost_id]

    return f'{stardust_cost:,}'.replace(',', ' ')


def calculate_evolution_cost(monster_id, evolution_id, evolutions):
    evolution_candy_costs = {
        12: [10, 13, 16, 265, 293, 519],
        25: [1, 4, 7, 19, 29, 32, 41, 43, 60, 63, 66, 69, 74, 92, 111, 116,
             133, 137, 147, 152, 155, 158, 161, 172, 173, 174, 175, 179, 187,
             236, 238, 239, 240, 246, 252, 255, 258, 270, 273, 280, 287, 304,
             328, 355, 363, 371, 374, 387, 390, 393, 396, 403, 406, 439, 440,
             443, 446, 495, 498, 501, 506, 535, 540, 543, 551, 574, 577, 599,
             607, 610, 650, 653, 656, 661, 704],
        50: [11, 14, 17, 21, 23, 25, 27, 35, 37, 39, 46, 48, 50, 52, 54, 56,
             58, 72, 77, 79, 81, 83, 84, 86, 88, 90, 95, 96, 98, 100, 102,
             104, 109, 113, 118, 120, 123, 138, 140, 163, 165, 167, 170, 177,
             191, 194, 204, 209, 216, 218, 220, 223, 228, 231, 261, 263, 266,
             268, 276, 278, 283, 285, 290, 294, 296, 300, 307, 309, 316, 318,
             322, 325, 331, 339, 341, 343, 345, 347, 353, 360, 361, 366, 399,
             400, 401, 408, 410, 412, 415, 418, 420, 425, 427, 431, 433, 436,
             438, 447, 449, 451, 453, 456, 458, 459, 504, 509, 511, 513, 515,
             520, 522, 524, 527, 529, 546, 548, 552, 554, 557, 559, 562, 564,
             566, 568, 572, 580, 585, 590, 595, 597, 605, 613, 622, 624, 627,
             629, 659, 667, 677, 674, 682, 684, 705, 688, 690, 692],
        100: [2, 5, 8, 33, 30, 42, 44, 61, 64, 67, 70, 75, 82, 93, 112, 117,
              125, 126, 148, 153, 156, 159, 176, 180, 188, 198, 200, 207, 215,
              233, 247, 253, 256, 259, 271, 274, 281, 288, 305, 315, 329, 349,
              356, 364, 372, 375, 388, 391, 394, 397, 404, 430, 444, 478, 496,
              499, 502, 507, 536, 541, 544, 575, 578, 600, 608, 611, 634, 651,
              654, 657, 662],
        400: [130, 320, 333, 808, 714]
    }
    evo_candy_cost = 0

    for cost in evolution_candy_costs:
        if int(monster_id) in evolution_candy_costs[cost]:
            evo_candy_cost += cost

    for evolution in evolutions:
        if int(evolution) == evolution_id:
            return evo_candy_cost
        for cost in evolution_candy_costs:
            if int(evolution) in evolution_candy_costs[cost]:
                evo_candy_cost += cost

    return evo_candy_cost


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
    great_id = monster_id
    great_candy = calculate_candy_cost(lvl, great_level)
    great_stardust = calculate_stardust_cost(lvl, great_level)

    ultra_product, ultra_cp, ultra_level = pokemon_rating(
        2500, monster, atk, de, sta, min_level(2500, monster),
        max_level(2500, monster))
    ultra_rating = 100 * (ultra_product / stats_ultra_product)
    ultra_id = monster_id
    ultra_candy = calculate_candy_cost(lvl, ultra_level)
    ultra_stardust = calculate_stardust_cost(lvl, ultra_level)

    if float(great_level) < lvl:
        great_rating = 0
    if float(ultra_level) < lvl:
        ultra_rating = 0

    evo_candy_cost = 0

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
            evo_candy_cost = calculate_evolution_cost(
                monster_id, evolution_id, evolutions)
            great_candy = calculate_candy_cost(
                lvl, great_level, evo_candy_cost)
            great_stardust = calculate_stardust_cost(
                lvl, great_level)

        if evo_ultra > ultra_rating:
            ultra_rating = evo_ultra
            ultra_cp = evo_ultra_cp
            ultra_level = evo_ultra_level
            ultra_id = evolution_id
            evo_candy_cost = calculate_evolution_cost(
                monster_id, evolution_id, evolutions)
            ultra_candy = calculate_candy_cost(
                lvl, ultra_level, evo_candy_cost)
            ultra_stardust = calculate_stardust_cost(
                lvl, ultra_level)

    return (float("{0:.2f}".format(great_rating)), great_id, great_cp,
            great_level, great_candy, great_stardust,
            float("{0:.2f}".format(ultra_rating)), ultra_id,
            ultra_cp, ultra_level, ultra_candy, ultra_stardust)

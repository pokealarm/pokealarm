import PokeAlarm.Utils as utils
import PokeAlarm.Locale as locale
import logging
import re
import json

log = logging.getLogger('PvpUtils')


def pokemon_rating(limit, monster_id, form_id, atk, de, sta,
                   min_level, max_level):
    multipliers = utils.get_cp_multipliers()
    base_stats = utils.get_base_stats(monster_id, form_id)
    highest_rating = 0
    highest_cp = 0
    highest_level = 0
    for level in range(int(min_level * 2), int((max_level + 0.5) * 2)):
        level = str(level / float(2)).replace(".0", "")
        cp = utils.calculate_cp(monster_id, form_id, atk, de, sta, level)
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


def calculate_candy_cost(start_level, target_level, evo_candy_cost=0):
    start_level = float(start_level)
    target_level = float(target_level)
    candy_table = utils.get_candy_costs()
    xl_candy_table = utils.get_xl_candy_costs()
    tmp_level = start_level
    candy_cost = evo_candy_cost
    xl_candy_cost = 0

    while tmp_level < target_level and tmp_level < 40:
        for cost_key in candy_table:
            lvls = re.findall(r"[\.\d]+", cost_key)
            if float(lvls[0]) <= tmp_level and tmp_level <= float(lvls[1]):
                candy_cost += candy_table[cost_key]
        tmp_level += 0.5

    while tmp_level < target_level and tmp_level < 50:
        for cost_key in xl_candy_table:
            lvls = re.findall(r"[\.\d]+", cost_key)
            if float(lvls[0]) <= tmp_level and tmp_level <= float(lvls[1]):
                xl_candy_cost += xl_candy_table[cost_key]
        tmp_level += 0.5

    if xl_candy_cost != 0:
        return f'{candy_cost:,} + {xl_candy_cost:,} XL'.replace(',', ' ')
    else:
        return f'{candy_cost:,}'.replace(',', ' ')


def calculate_stardust_cost(start_level, target_level):
    start_level = float(start_level)
    target_level = float(target_level)
    stardust_table = utils.get_stardust_costs()

    tmp_level = start_level
    stardust_cost = 0
    while tmp_level < target_level and tmp_level < 50:
        for cost_key in stardust_table:
            lvls = re.findall(r"[\.\d]+", cost_key)
            if float(lvls[0]) <= tmp_level and tmp_level <= float(lvls[1]):
                stardust_cost += stardust_table[cost_key]
        tmp_level += 0.5

    return f'{stardust_cost:,}'.replace(',', ' ')


def calculate_evolution_cost(monster_id, target_id, evolutions,
                             evolution_costs):
    if monster_id == target_id or not ([True for s in evolutions
                                        if f"{target_id}_" in s]):
        return 0
    evo_candy_cost = evolution_costs[0]

    for evolution in evolutions:
        evo_id, evo_form_id = re.findall(r"[\.\d]+", evolution)
        evo_id = int(evo_id)
        evo_form_id = int(evo_form_id)

        if evo_id == target_id:
            return evo_candy_cost
        evo_candy_cost += evolution_costs[1]

    return evo_candy_cost


def get_pvp_info(monster_id, form_id, atk, de, sta, lvl):
    lvl = float(lvl)

    best_great_product = utils.get_best_great_product(monster_id, form_id)
    best_ultra_product = utils.get_best_ultra_product(monster_id, form_id)

    evolutions = utils.get_evolutions(monster_id, form_id, True)
    evolution_costs = utils.get_evolution_costs(monster_id, form_id)

    great_product, great_cp, great_level = pokemon_rating(
        1500, monster_id, form_id, atk, de, sta, utils.min_level(
            1500, monster_id, form_id),
        utils.max_level(1500, monster_id, form_id))
    great_rating = 100 * (great_product / best_great_product)
    great_id = monster_id
    great_candy = calculate_candy_cost(lvl, great_level)
    great_stardust = calculate_stardust_cost(lvl, great_level)
    great_rank = get_pvp_rank(monster_id, form_id, 1500)

    ultra_product, ultra_cp, ultra_level = pokemon_rating(
        2500, monster_id, form_id, atk, de, sta, utils.min_level(
            2500, monster_id, form_id),
        utils.max_level(2500, monster_id, form_id))
    ultra_rating = 100 * (ultra_product / best_ultra_product)
    ultra_id = monster_id
    ultra_candy = calculate_candy_cost(lvl, ultra_level)
    ultra_stardust = calculate_stardust_cost(lvl, ultra_level)
    ultra_rank = get_pvp_rank(monster_id, form_id, 2500)

    if float(great_level) < lvl:
        great_rating = 0
    if float(ultra_level) < lvl:
        ultra_rating = 0

    evo_candy_cost = 0

    for evolution in evolutions:
        evo_id, evo_form_id = re.findall(r"[\.\d]+", evolution)
        evo_id = int(evo_id)
        evo_form_id = int(evo_form_id)

        best_great_product = utils.get_best_great_product(
            evo_id, evo_form_id)
        best_ultra_product = utils.get_best_ultra_product(
            evo_id, evo_form_id)

        great_product, evo_great_cp, evo_great_level = pokemon_rating(
            1500, evo_id, evo_form_id, atk, de, sta, utils.min_level(
                1500, evo_id, evo_form_id),
            utils.max_level(1500, evo_id, evo_form_id))
        ultra_product, evo_ultra_cp, evo_ultra_level = pokemon_rating(
            2500, evo_id, evo_form_id, atk, de, sta, utils.min_level(
                2500, evo_id, evo_form_id),
            utils.max_level(2500, evo_id, evo_form_id))

        evo_great_rank = get_pvp_rank(evo_id, evo_form_id, 1500)
        evo_ultra_rank = get_pvp_rank(evo_id, evo_form_id, 2500)

        evo_great = 100 * (great_product / best_great_product)
        evo_ultra = 100 * (ultra_product / best_ultra_product)

        if float(evo_great_level) < lvl:
            evo_great = 0
        if float(evo_ultra_level) < lvl:
            evo_ultra = 0

        if evo_great > great_rating:
            great_rating = evo_great
            great_cp = evo_great_cp
            great_level = evo_great_level
            great_id = evo_id
            great_rank = evo_great_rank
            evo_candy_cost = calculate_evolution_cost(
                monster_id, evo_id, evolutions, evolution_costs)
            great_candy = calculate_candy_cost(
                lvl, great_level, evo_candy_cost)
            great_stardust = calculate_stardust_cost(
                lvl, great_level)

        if evo_ultra > ultra_rating:
            ultra_rating = evo_ultra
            ultra_cp = evo_ultra_cp
            ultra_level = evo_ultra_level
            ultra_id = evo_id
            ultra_rank = evo_ultra_rank
            evo_candy_cost = calculate_evolution_cost(
                monster_id, evo_id, evolutions, evolution_costs)
            ultra_candy = calculate_candy_cost(
                lvl, ultra_level, evo_candy_cost)
            ultra_stardust = calculate_stardust_cost(
                lvl, ultra_level)

    return (float("{0:.2f}".format(great_rating)), great_id, great_cp,
            great_level, great_candy, great_stardust, great_rank,
            float("{0:.2f}".format(ultra_rating)), ultra_id, ultra_cp,
            ultra_level, ultra_candy, ultra_stardust, ultra_rank)


def get_pvp_rank(monster_id, form_id, maxcp):
    if not hasattr(get_pvp_rank, 'info'):
        get_pvp_rank.info = {}
    if not hasattr(get_pvp_rank.info, f'cp{maxcp}'):
        get_pvp_rank.info[f'cp{maxcp}'] = {}
        file_ = utils.get_path(f'data/rankings-{maxcp}.json')
        with open(file_, 'r') as f:
            j = json.load(f)
            f.close()
            rank_number = 1
            for id_ in j:
                mon_and_form_array = re.split(
                    r' \(|\)', id_.get('speciesName'))
                if len(mon_and_form_array) == 1:
                    mon_and_form_array.append("Normal")
                elif len(mon_and_form_array) == 3:
                    mon_and_form_array.pop(2)
                mon_and_form_str = '_'.join(mon_and_form_array)
                get_pvp_rank.info[f'cp{maxcp}'][mon_and_form_str] = rank_number
                rank_number += 1

    loc = locale.Locale('en')
    mon_name = loc.get_english_pokemon_name(monster_id)
    form_name = loc.get_english_form_name(monster_id, form_id)
    form_name = form_name.replace("Alola", "Alolan")

    return get_pvp_rank.info[f'cp{maxcp}'].get(
        f"{mon_name}_{form_name}", '\u221E')

import PokeAlarm.Utils as utils
import logging
import json

log = logging.getLogger("PvpUtils")


def pokemon_rating(limit, monster_id, form_id, atk, de, sta):
    multipliers = utils.get_cp_multipliers()
    multiplier_squares = utils.get_cp_multiplier_squares()
    base_stats = utils.get_base_stats(monster_id, form_id)
    cp_base = utils.calculate_cp_base(monster_id, form_id, atk, de, sta)

    if cp_base == 0:
        return 0.0, 0, 0

    max_cp = int(cp_base * multiplier_squares[50])
    if max_cp <= limit:
        best_cp, best_level = max_cp, 50
    else:
        best_cp, best_level = utils.bisect_levels(limit, cp_base, 1, 49.5)

    attack = (base_stats["attack"] + atk) * multipliers[best_level]
    defense = (base_stats["defense"] + de) * multipliers[best_level]
    stamina = int((base_stats["stamina"] + sta) * multipliers[best_level])
    product = attack * defense * stamina

    return product, best_cp, best_level


def get_pvp_info(monster_id, form_id, atk, de, sta, lvl):
    lvl = float(lvl)

    best_great_product = utils.get_best_great_product(monster_id, form_id)
    best_ultra_product = utils.get_best_ultra_product(monster_id, form_id)

    evolutions = utils.get_evolutions(monster_id, form_id)
    evolution_costs = utils.get_evolution_costs(monster_id, form_id)

    great_product, great_cp, great_level = pokemon_rating(
        1500, monster_id, form_id, atk, de, sta
    )
    great_rating = (
        0 if best_great_product == 0 else 100 * (great_product / best_great_product)
    )
    great_id = monster_id

    great_candy = utils.calculate_candy_cost(lvl, great_level)
    great_stardust = utils.calculate_stardust_cost(lvl, great_level)

    great_rank = get_pvp_rank(monster_id, form_id, 1500)

    ultra_product, ultra_cp, ultra_level = pokemon_rating(
        2500, monster_id, form_id, atk, de, sta
    )
    ultra_rating = (
        0 if best_ultra_product == 0 else 100 * (ultra_product / best_ultra_product)
    )
    ultra_id = monster_id

    ultra_candy = utils.calculate_candy_cost(lvl, ultra_level)
    ultra_stardust = utils.calculate_stardust_cost(lvl, ultra_level)

    ultra_rank = get_pvp_rank(monster_id, form_id, 1500)

    if float(great_level) < lvl:
        great_rating = 0
    if float(ultra_level) < lvl:
        ultra_rating = 0

    evo_candy_cost = 0

    for evo_id, evo_form_id in evolutions:
        best_great_product = utils.get_best_great_product(evo_id, evo_form_id)
        best_ultra_product = utils.get_best_ultra_product(evo_id, evo_form_id)

        great_product, evo_great_cp, evo_great_level = pokemon_rating(
            1500, evo_id, evo_form_id, atk, de, sta
        )
        ultra_product, evo_ultra_cp, evo_ultra_level = pokemon_rating(
            2500, evo_id, evo_form_id, atk, de, sta
        )

        evo_great_rank = get_pvp_rank(evo_id, evo_form_id, 1500)
        evo_ultra_rank = get_pvp_rank(evo_id, evo_form_id, 2500)

        evo_great = (
            0 if best_great_product == 0 else 100 * (great_product / best_great_product)
        )

        evo_ultra = (
            0 if best_ultra_product == 0 else 100 * (ultra_product / best_ultra_product)
        )

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
            evo_candy_cost = utils.calculate_evolution_cost(
                monster_id, evo_id, evolutions, evolution_costs
            )
            great_candy = utils.calculate_candy_cost(lvl, great_level, evo_candy_cost)
            great_stardust = utils.calculate_stardust_cost(lvl, great_level)

        if evo_ultra > ultra_rating:
            ultra_rating = evo_ultra
            ultra_cp = evo_ultra_cp
            ultra_level = evo_ultra_level
            ultra_id = evo_id
            ultra_rank = evo_ultra_rank
            evo_candy_cost = utils.calculate_evolution_cost(
                monster_id, evo_id, evolutions, evolution_costs
            )
            ultra_candy = utils.calculate_candy_cost(lvl, ultra_level, evo_candy_cost)
            ultra_stardust = utils.calculate_stardust_cost(lvl, ultra_level)

    return (
        float(f"{great_rating:.2f}"),
        great_id,
        great_cp,
        great_level,
        great_candy,
        great_stardust,
        great_rank,
        float(f"{ultra_rating:.2f}"),
        ultra_id,
        ultra_cp,
        ultra_level,
        ultra_candy,
        ultra_stardust,
        ultra_rank,
    )


def get_pvp_rank(monster_id, form_id, maxcp):
    try:
        get_pvp_rank.info
    except AttributeError:
        get_pvp_rank.info = {}
    try:
        get_pvp_rank.info[maxcp]
    except IndexError:
        get_pvp_rank.info[maxcp] = {}
        file_ = utils.get_path(f"data/rankings-{maxcp}.json")
        with open(file_, "r") as f:
            j = json.load(f)
            f.close()
        rank_number = 1
        for id_ in j:
            if "(" in id_.get("speciesName"):
                get_pvp_rank.info[maxcp][id_.get("speciesId")] = rank_number
            else:
                get_pvp_rank.info[maxcp][f"{id_.get('speciesId')}_normal"] = rank_number
            rank_number += 1

    mon_proto = utils.get_proto_name(monster_id, form_id)
    return get_pvp_rank.info[maxcp].get(mon_proto, 9999)

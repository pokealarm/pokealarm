import PokeAlarm.Utils as utils
import logging
import re

log = logging.getLogger("PvpUtils")


def pokemon_rating(limit, monster_id, form_id, atk, de, sta, min_level, max_level):
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
            stamina = int(((base_stats["stamina"] + sta) * (multipliers[str(level)])))
            product = attack * defense * stamina
            if product > highest_rating:
                highest_rating = product
                highest_cp = cp
                highest_level = level
    return highest_rating, highest_cp, highest_level


def get_pvp_info(monster_id, form_id, atk, de, sta, lvl):
    lvl = float(lvl)

    best_great_product = utils.get_best_great_product(monster_id, form_id)
    best_ultra_product = utils.get_best_ultra_product(monster_id, form_id)

    evolutions = utils.get_evolutions(monster_id, form_id, True)
    evolution_costs = utils.get_evolution_costs(monster_id, form_id)

    great_product, great_cp, great_level = pokemon_rating(
        1500,
        monster_id,
        form_id,
        atk,
        de,
        sta,
        utils.min_level(1500, monster_id, form_id),
        utils.max_level(1500, monster_id, form_id),
    )
    great_rating = (
        0 if best_great_product == 0 else 100 * (great_product / best_great_product)
    )
    great_id = monster_id
    great_candy = utils.calculate_candy_cost(lvl, great_level)
    great_stardust = utils.calculate_stardust_cost(lvl, great_level)

    ultra_product, ultra_cp, ultra_level = pokemon_rating(
        2500,
        monster_id,
        form_id,
        atk,
        de,
        sta,
        utils.min_level(2500, monster_id, form_id),
        utils.max_level(2500, monster_id, form_id),
    )
    ultra_rating = (
        0 if best_ultra_product == 0 else 100 * (ultra_product / best_ultra_product)
    )
    ultra_id = monster_id
    ultra_candy = utils.calculate_candy_cost(lvl, ultra_level)
    ultra_stardust = utils.calculate_stardust_cost(lvl, ultra_level)

    if float(great_level) < lvl:
        great_rating = 0
    if float(ultra_level) < lvl:
        ultra_rating = 0

    evo_candy_cost = 0

    for evolution in evolutions:
        evo_id, evo_form_id = re.findall(r"[\.\d]+", evolution)
        evo_id = int(evo_id)
        evo_form_id = int(evo_form_id)

        best_great_product = utils.get_best_great_product(evo_id, evo_form_id)
        best_ultra_product = utils.get_best_ultra_product(evo_id, evo_form_id)

        great_product, evo_great_cp, evo_great_level = pokemon_rating(
            1500,
            evo_id,
            evo_form_id,
            atk,
            de,
            sta,
            utils.min_level(1500, evo_id, evo_form_id),
            utils.max_level(1500, evo_id, evo_form_id),
        )
        ultra_product, evo_ultra_cp, evo_ultra_level = pokemon_rating(
            2500,
            evo_id,
            evo_form_id,
            atk,
            de,
            sta,
            utils.min_level(2500, evo_id, evo_form_id),
            utils.max_level(2500, evo_id, evo_form_id),
        )

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
            evo_candy_cost = utils.calculate_evolution_cost(
                monster_id, evo_id, evolutions, evolution_costs
            )
            ultra_candy = utils.calculate_candy_cost(lvl, ultra_level, evo_candy_cost)
            ultra_stardust = utils.calculate_stardust_cost(lvl, ultra_level)

    return (
        float("{0:.2f}".format(great_rating)),
        great_id,
        great_cp,
        great_level,
        great_candy,
        great_stardust,
        float("{0:.2f}".format(ultra_rating)),
        ultra_id,
        ultra_cp,
        ultra_level,
        ultra_candy,
        ultra_stardust,
    )

import json
import sys
import os
import itertools
import requests


class PVP:
    def __init__(self, pa_root):
        # Fetch pokemon data
        master_file = (
            "https://raw.githubusercontent.com/WatWowMap/"
            "Masterfile-Generator/master/master-latest-everything.json"
        )
        master_file = requests.get(master_file)
        monster_data = master_file.json()["pokemon"]
        with open(pa_root + "/data/pokemon_data.json", "w") as f:
            json.dump(monster_data, f, indent=2)
            f.close()

        # Calculate PvP products
        monster_forms = utils.get_raw_form_names()
        cp_multipliers = utils.get_cp_multipliers()

        monster_products = {}

        for id_ in monster_forms:
            monster_products[id_] = {}
            for form_id_ in monster_forms[id_]:
                monster_products[id_][form_id_] = {}
                for limit in [1500, 2500]:
                    highest_product = self.spreads(
                        limit,
                        id_,
                        form_id_,
                        self.min_level(limit, id_, form_id_),
                        self.max_level(limit, id_, form_id_),
                        cp_multipliers,
                    )

                    monster_products[id_][form_id_][
                        f"{limit}_highest_product"
                    ] = highest_product

                    print(
                        f"{id_}_{form_id_}: highest product at {limit}: {highest_product}"
                    )

        with open(pa_root + "/tools/generated_stat_products.json", "w+") as f:
            json.dump(monster_products, f, indent=2)
            f.close()

    @staticmethod
    def max_level(cp_limit, monster_id, form_id=0):
        if utils.max_cp(monster_id, form_id) <= cp_limit:
            return 50.0

        cp_base = utils.calculate_cp_base(monster_id, form_id, 0, 0, 0)
        cp, lvl = utils.bisect_levels(cp_limit, cp_base, 1, 50)
        return min(lvl + 1, 50)

    @staticmethod
    def min_level(cp_limit, monster_id, form_id=0):
        if utils.max_cp(monster_id, form_id) <= cp_limit:
            return 50.0

        cp_base = utils.calculate_cp_base(monster_id, form_id, 15, 15, 15)
        cp, lvl = utils.bisect_levels(cp_limit, cp_base, 1, 50)
        return max(lvl - 1, 1)

    @staticmethod
    def spreads(limit, monster_id, form_id, min_level, max_level, cp_multipliers):
        base_stats = utils.get_base_stats(monster_id, form_id)
        highest_product = 0

        for iv in itertools.product(range(16), range(16), range(16)):
            cp_base = utils.calculate_cp_base(monster_id, form_id, iv[0], iv[1], iv[2])
            cp, level = utils.bisect_levels(limit, cp_base, min_level, max_level)
            if cp == 0:
                continue

            attack = (base_stats["attack"] + iv[0]) * cp_multipliers[level]
            defense = (base_stats["defense"] + iv[1]) * cp_multipliers[level]
            stamina = int((base_stats["stamina"] + iv[2]) * cp_multipliers[level])
            product = attack * defense * stamina

            if product > highest_product:
                highest_product = product

        return highest_product


if __name__ == "__main__" and __package__ is None:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    import PokeAlarm.Utils as utils

    PVP(root)

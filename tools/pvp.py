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
                    highest, lowest = self.spreads(
                        limit,
                        id_,
                        form_id_,
                        utils.min_level(limit, id_, form_id_),
                        utils.max_level(limit, id_, form_id_),
                        cp_multipliers,
                    )

                    monster_products[id_][form_id_][
                        "{}_highest_product".format(limit)
                    ] = highest["product"]
                    monster_products[id_][form_id_][
                        "{}_lowest_product".format(limit)
                    ] = lowest["product"]

                    print(
                        "{}_{}: highest product at {}: {}".format(
                            id_, form_id_, limit, highest["product"]
                        )
                    )
                    print(
                        "{}_{}: lowest product at {}: {}".format(
                            id_, form_id_, limit, lowest["product"]
                        )
                    )

        with open(pa_root + "/tools/generated_stat_products.json", "w+") as f:
            json.dump(monster_products, f, indent=2)
            f.close()

    @staticmethod
    def spreads(limit, monster_id, form_id, min_level, max_level, cp_multipliers):
        smallest = {"product": 999999999}
        highest = {"product": 0}

        for level in range(int(min_level * 2), int((max_level + 0.5) * 2)):
            level = str(level / 2).replace(".0", "")

            for stat_product in itertools.product(range(16), range(16), range(16)):
                cp = utils.calculate_cp(
                    monster_id,
                    form_id,
                    stat_product[0],
                    stat_product[1],
                    stat_product[2],
                    level,
                )
                if cp > limit:
                    continue
                base_stats = utils.get_base_stats(monster_id, form_id)
                attack = (base_stats["attack"] + stat_product[0]) * (
                    cp_multipliers[str(level)]
                )
                defense = (base_stats["defense"] + stat_product[1]) * (
                    cp_multipliers[str(level)]
                )
                stamina = int(
                    (
                        (base_stats["stamina"] + stat_product[2])
                        * (cp_multipliers[str(level)])
                    )
                )
                product = attack * defense * stamina
                if product > highest["product"]:
                    highest.update(
                        {
                            "product": product,
                            "attack": attack,
                            "defense": defense,
                            "stamina": stamina,
                            "atk": stat_product[0],
                            "de": stat_product[1],
                            "sta": stat_product[2],
                            "cp": cp,
                            "level": level,
                        }
                    )
                if product < smallest["product"]:
                    smallest.update(
                        {
                            "product": product,
                            "attack": attack,
                            "defense": defense,
                            "stamina": stamina,
                            "atk": stat_product[0],
                            "de": stat_product[1],
                            "sta": stat_product[2],
                            "cp": cp,
                            "level": level,
                        }
                    )
        return highest, smallest


if __name__ == "__main__" and __package__ is None:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    import PokeAlarm.Utils as utils

    PVP(root)

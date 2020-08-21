import json
import sys
import os
import itertools


class PVP:
    def __init__(self, pa_root):
        with open(pa_root + "/data/base_stats.json", "r") as json_data:
            stats = json.load(json_data)
            json_data.close()

        multipliers = utils.get_cp_multipliers()

        for json_mon in list(stats.keys()):
            for limit in [1500, 2500]:
                highest, lowest = self.spreads(
                    limit, json_mon, min_level(limit, json_mon),
                    max_level(limit, json_mon), multipliers, stats)
                stats[json_mon]["{}_product".format(limit)] \
                    = highest["product"]
                print(("{}: highest product at {}: {}".format(
                    json_mon, limit, highest['product'])))

        with open(pa_root + "/tools/stats_with_products.json", "w+") as f:
            json.dump(stats, f, indent=2)
            f.close()

    @staticmethod
    def spreads(limit, mon, min_level, max_level, multipliers, stats):
        smallest = {"product": 999999999}
        highest = {"product": 0}

        for level in range(int(min_level * 2), int((max_level + 0.5) * 2)):
            level = str(level / 2).replace('.0', '')

            for stat_product in \
                    itertools.product(range(16), range(16), range(16)):
                cp = calculate_cp(mon, stat_product[0], stat_product[1],
                                  stat_product[2], level)
                if cp > limit:
                    continue

                attack = ((stats[mon]["attack"] + stat_product[0]) * (
                    multipliers[str(level)]))
                defense = ((stats[mon]["defense"] + stat_product[1]) * (
                    multipliers[str(level)]))
                stamina = ((stats[mon]["stamina"] + stat_product[2]) * (
                    multipliers[str(level)]))
                product = (attack * defense * stamina)
                if product > highest["product"]:
                    highest.update({
                        'product': product,
                        'attack': attack,
                        'defense': defense,
                        'stamina': stamina,
                        'atk': stat_product[0],
                        'de': stat_product[1],
                        'sta': stat_product[2],
                        'cp': cp,
                        'level': level
                    })
                if product < smallest["product"]:
                    smallest.update({
                        'product': product,
                        'attack': attack,
                        'defense': defense,
                        'stamina': stamina,
                        'atk': stat_product[0],
                        'de': stat_product[1],
                        'sta': stat_product[2],
                        'cp': cp,
                        'level': level
                    })
        return highest, smallest


if __name__ == '__main__' and __package__ is None:
    sys.path.append(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    from PokeAlarm.Utilities.PvpUtils import calculate_cp, max_level, min_level
    import PokeAlarm.Utils as utils

    PVP(root)

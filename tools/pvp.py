import json
import sys
import os
from math import sqrt

PAROOT = str(os.path.abspath(os.path.dirname(__file__))).replace("/tools", "")
sys.path.append(PAROOT)
from PokeAlarm.Utilities.PvpUtils import mon, calculate_cp, max_cp, max_level, min_level
import PokeAlarm.Utils as utils

def spreads(limit, mon, min_level, max_level):
    smallest = { "product": 999999999 }
    highest = { "product": 0 }
    for level in range(int(min_level * 2), int((max_level + 0.5) * 2)):
        level = str(level / 2).replace(".0", "")
        for atk in range(16):
            for de in range(16):
               for sta in range(16):
                   cp = calculate_cp(mon, atk, de, sta, level)
                   if not cp > limit:
                       attack = ((stats[mon]["attack"] + atk) * (multipliers[str(level)]))
                       defense = ((stats[mon]["defense"] + de) * (multipliers[str(level)]))
                       stamina = int(((stats[mon]["stamina"] + sta) * (multipliers[str(level)])))
                       product = (attack * defense * stamina)
                       if product > highest["product"]:
                           highest["product"] = product
                           highest["attack"] = attack
                           highest["defense"] = defense
                           highest["stamina"] = stamina
                           highest["atk"] = atk
                           highest["de"] = de
                           highest["sta"] = sta
                           highest["cp"] = cp
                           highest["level"] = level
                       if product < smallest["product"]:
                           smallest["product"] = product
                           smallest["attack"] = attack
                           smallest["defense"] = defense
                           smallest["stamina"] = stamina
                           smallest["atk"] = atk
                           smallest["de"] = de
                           smallest["sta"] = sta
                           smallest["cp"] = cp
                           smallest["level"] = level
    return highest, smallest


with open(PAROOT + "/data/base_stats.json", "r") as json_data:
    stats = json.load(json_data)
    json_data.close()

multipliers = utils.get_cp_multipliers()

for json_mon in stats.keys():
    json_mon = mon(json_mon)
    for limit in [1500, 2500]:
        highest, lowest = spreads(limit, json_mon, min_level(limit, json_mon), max_level(limit, json_mon))
        stats[json_mon][str(limit) + "_product"] = highest["product"]
        print(str(mon(json_mon)) + ": highest product at " + str(limit) + ": " + str(highest["product"]))

with open("stats_with_products.json", "w") as f:
    json.dump(stats, f, indent=2)
    f.close()

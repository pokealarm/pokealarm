# -*- coding: utf-8 -*-

"""
pokealarm.utils._data_files
~~~~~~~~~~~~~~~~

Contains information for accessing info from pokealarm/data.
"""

# Standard Library Imports
import os
import json
from collections import defaultdict
# 3rd Party Imports
from future.utils import iteritems
# Local Imports
from prototype import _ROOT_PATH


def _load_monster_stats():
    filepath = os.path.join(_ROOT_PATH, "data/mon_stats.json")
    with open(filepath, 'r') as f:
        contents = json.loads(f.read())
    data = defaultdict(dict)
    for mon_id, stats in iteritems(contents):
        mon_id = int(mon_id)
        for stat, val in iteritems(stats):
            data[str(stat)][mon_id] = val
    return data


mon_stats = _load_monster_stats()

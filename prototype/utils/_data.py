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


def _load_stats(filename):
    filepath = os.path.join(_ROOT_PATH, filename)
    with open(filepath, 'r') as f:
        contents = json.loads(f.read())
    data = defaultdict(dict)
    for id_, stats in iteritems(contents):
        id_ = int(id_)
        for stat, val in iteritems(stats):
            data[str(stat)][id_] = val
    return data


mon_stats = _load_stats("data/mon_stats.json")
move_stats = _load_stats("data/move_stats.json")

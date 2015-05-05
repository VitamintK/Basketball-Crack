import json
import math

from config import root_dir
from collections import defaultdict

import json_sets

json_dir = root_dir + 'json/'
default_game_set = json_sets.medium

percentile_file = 'percentiles.json'

def generate_stat_dicts(dataset = default_game_set):
    stat_sets = defaultdict(list)
    for player in default_game_set:
        with open('{}{}'.format(json_dir,player)) as pjson:
            player_json = json.load(pjson)
        for row in player_json['per_game'][1:]:
            if row[0] == 'Career':
                break
            for index, stat in enumerate(row):
                try:
                    statint = float(stat)
                    stat_sets[player_json['per_game'][0][index]].append(statint)
                except:
                    pass
                    #statint = stat
    return {stat:sorted(stats) for stat, stats in stat_sets.items()}

def generate_percentiles(step = 0.05, stat_dict=generate_stat_dicts()):
    assert step <= 1
    stat_percentiles = defaultdict(list)
    for stat, stats in stat_dict.items():
        cur_step = 0
        while cur_step <= 1:
            stat_percentiles[stat].append(( cur_step, stats[math.floor(cur_step * len(stats))]))
            cur_step += step
    return stat_percentiles

def get_percentile(my_num, stat_cat, percentiles = generate_percentiles()):
    percentile = 0
    for i in percentiles[stat_cat]:
        if my_num < i[1]:
            return percentile
        percentile = i[0]
    return 1

def make_color(percentile):
    if percentile > 0.5:
        return "rgb(0,{},0)".format(math.floor(255*((percentile - 0.5)/0.5)))
    elif percentile == 0.5:
        return "rgb(0,0,0)"
    else:
        return "rgb({},0,0)".format(math.floor(255*((0.5 - percentile)/0.5)))

print(make_color(get_percentile(15, 'PTS')))
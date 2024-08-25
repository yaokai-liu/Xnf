import json
import networkx as nx


with open('machine-compact.json', 'r') as fp:
    j = json.load(fp)

assert isinstance(j, dict)
state_map = dict()
for k in j.keys():
    state_map[k] = len(state_map)
table = dict()
for k in j.keys():
    steps = dict()
    for p in j[k]:
        if j[k].startswith('('):
            steps[p] = state_map[j[k]]
        else:
            steps[p] = j[k]
    table[state_map[k]] = steps


import argparse
import os
import pickle

import sys

from code.auxilliaries.virtuoso_graph_reader import VirtuosoGraphReader

parser = argparse.ArgumentParser(description='Extract gold relations from a conll file.')
parser.add_argument('--relation_file')
parser.add_argument('--entity_file')
parser.add_argument('--cache')
args = parser.parse_args()

graph_reader = VirtuosoGraphReader()

#Load cache file
cachefile = args.cache
if os.path.exists(cachefile):
    with open(cachefile, 'rb') as cachehandle:
        print("using cached result from '%s'" % cachefile, file=sys.stderr)
        rel_cache = pickle.load(cachehandle)
else:
    rel_cache = {}

def get_indexes(key, e_dict, rel_cache):
    if key in rel_cache:
        return rel_cache[key]

    parts = key.split("\t")
    entity = parts[0]
    relation_1 = parts[1]
    relation_2 = parts[2]

    returned_indexes = []
    predicted_entities = graph_reader.query(entity, relation_1, relation_2, skip_names=True)
    for entity in predicted_entities:
        entity = entity.strip()
        if entity in e_dict:
            returned_indexes.append(e_dict[entity][0])
        else:
            idx = len(e_dict)
            e_names = [name.replace("\n", "") for name in graph_reader.get_names(entity)]
            e_types = graph_reader.get_types(entity)

            e_dict[entity] = [idx, [str(idx), entity, "|".join(e_names), "|".join(e_types)]]

            returned_indexes.append(idx)

    rel_cache[key] = returned_indexes
    return returned_indexes

# Read in the already found entities:
counter = 0
e_dict = {}
with open(args.entity_file, 'r') as e_file:
    for line in e_file:
        line = line.strip()
        if line:
            parts = line.split("\t")

            if len(parts) == 1:
                parts += ["", "", ""]
            elif len(parts) == 2:
                parts += ["", ""]
            elif len(parts) == 3:
                parts += [""]

            e_dict[parts[1]] = [counter, parts]

            counter += 1

first = True
counter = 0
with open(args.relation_file, 'r') as r_file:
    for line in r_file:
        line = line.strip()

        if first:
            first = False
        else:
            print("")

        if line:
            parts = line.split("\t")
            entity = parts[0]
            relation_1 = parts[2]
            relation_2 = parts[3]

            cache_key = "\t".join([entity, relation_1, relation_2])
            returned_indexes = get_indexes(cache_key, e_dict, rel_cache)
            returned_indexes = [str(x) for x in returned_indexes]

            new_line_parts = parts + [",".join(returned_indexes)]

            print("\t".join(new_line_parts), end="")
        else:
            counter += 1
            print(line, end="")
            print("Gathering entity info for question #"+str(counter), end="\r", file=sys.stderr)

# write to cache file
with open(cachefile, 'wb') as cachehandle:
    print("\nsaving relation cache as '%s'" % cachefile, file=sys.stderr)
    pickle.dump(rel_cache, cachehandle)

organized_dict = sorted(e_dict.values(), key=lambda x: x[0])

first = True
with open(args.entity_file, 'w') as e_file:
    for idx, entity_line in organized_dict:
        print("Writing entity #"+str(idx) + ": " + entity_line[1], end="\r", file=sys.stderr)
        entity_str = entity_line[0]
        entity_str += "\t" + entity_line[1]
        entity_str += "\t" + entity_line[2]
        entity_str += "\t" + entity_line[3]

        if first:
            first = False
        else:
            print("", file=e_file)

        print(entity_str, file=e_file, end="")

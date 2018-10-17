import argparse

from code.auxilliaries.graph_reader import GraphReader
from code.auxilliaries.virtuoso_graph_reader import VirtuosoGraphReader
import sys

parser = argparse.ArgumentParser(description='Predict entities from a relation file.')
parser.add_argument('--input_file')
parser.add_argument('--entity_file')
args = parser.parse_args()

mid_prefix = "http://rdf.freebase.com/ns/m."

entity_map = []
bug_offset = 0
with open(args.entity_file, 'r') as e_file:
    for line in e_file:
        line = line.strip()
        if line:
            parts = line.split("\t")

            if not parts[1].startswith(mid_prefix):
                gold_entities = [parts[1]]
            elif len(parts) == 2:
                gold_entities = []
            else:
                gold_entities = parts[2].split("|")

            idx = int(parts[0])
            if idx != len(entity_map) + bug_offset:
                print(idx, file=sys.stderr)
                print("BUG", file=sys.stderr)
                bug_offset = idx - len(entity_map)
                print(bug_offset, file=sys.stderr)
                print("---", file=sys.stderr)

            entity_map.append(gold_entities)


first = True
q_pointer = 1
with open(args.input_file, 'r') as pred_file:
    for line in pred_file:
        if first:
            first = False
        else:
            print("")
        line = line.strip()

        if not line or line == "None":
            continue
        else:
            print("Computing prediction for question #" + str(q_pointer), end="\r", file=sys.stderr)
            q_pointer += 1

            parts = line.split("\t")
            target_entity_indexes = parts[4].split(",") if len(parts) == 5 else []

            target_entities = []
            for index in target_entity_indexes:
                target_entities.extend(entity_map[int(index)])

            print("\t".join(target_entities), end="")


print("" + str(q_pointer), end="\n", file=sys.stderr)
import argparse

from code.auxilliaries.graph_reader import GraphReader

parser = argparse.ArgumentParser(description='Predict entities from a relation file.')
parser.add_argument('--input_file')
args = parser.parse_args()

graph_name = "data/toy-125/toy.graph"
graph_reader = GraphReader(graph_name)


first = True
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
            parts = line.split("\t")
            entity = parts[0]
            rel1 = parts[1]
            rel2 = parts[2]

            predicted_entity = graph_reader.query(entity, rel1, rel2)
            print(",".join(predicted_entity), end="")
import argparse

from code.auxilliaries.graph_reader import GraphReader

parser = argparse.ArgumentParser(description='Extract gold relations from a conll file.')
parser.add_argument('--input_file')
args = parser.parse_args()

graph_name = "data/toy-125/toy.graph"
graph_reader = GraphReader(graph_name)

entities = []
golds = []
reading = 0

with open(args.input_file, 'r') as i_file:
    for line in i_file:
        line = line.strip()
        if line and reading == 0:
            pass
        elif line and reading == 1:
            parts = line.split("\t")
            entities.append(parts[2])
        elif line and reading == 2:
            parts = line.split("\t")
            golds.append(parts[0])
        elif not line and reading == 2:
            max_f1 = 0.0
            best_output = "UNK\tUNK\tUNK"
            for entity in entities:
                best_edge, f1_score = graph_reader.get_optimal_edge(entity, golds)
                if f1_score > max_f1:
                    max_f1 = f1_score
                    best_output = entity + "\t" + best_edge
            print(best_output)

            entities = []
            golds = []

        if not line:
            reading = (reading + 1) % 3
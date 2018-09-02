import argparse

from code.auxilliaries.graph_reader import GraphReader

parser = argparse.ArgumentParser(description='Extract gold relations from a conll file.')
parser.add_argument('--input_file')
args = parser.parse_args()

graph_name = "data/toy-125/toy.graph"
graph_reader = GraphReader(graph_name)

entities = []
scores = []
golds = []
reading = 0

def print_lines(rel_lines):
    formatted_rel_lines = ["\t".join(line) for line in rel_lines]
    print("\n".join(formatted_rel_lines), end="")

first = True
should_proceed = True
printed_nothing = False


def process_gathered_entities():
    max_f1 = 0.0
    suboptimal = []
    optimal = []
    for entity, score in zip(entities, scores):
        best_edges, f1_score = graph_reader.get_all_optimal_edges(entity, golds)
        other_edges = graph_reader.get_suboptimal_edges(entity, golds)
        suboptimal.extend([[entity, score, edge] for edge in other_edges])
        if f1_score > max_f1:
            max_f1 = f1_score
            suboptimal.extend(optimal)
            optimal = [[entity, score, edge] for edge in best_edges]
        elif f1_score == max_f1:
            optimal.extend([[entity, score, edge] for edge in best_edges])
        else:
            suboptimal.extend([[entity, score, edge] for edge in best_edges])
    print_lines([line + ["True"] for line in optimal])
    if len(optimal) > 0 and len(suboptimal) > 0:
        print("")
    print_lines([line + ["False"] for line in suboptimal])

    return optimal, suboptimal


with open(args.input_file, 'r') as i_file:
    for line in i_file:
        line = line.strip()
        if line and reading == 0:
            if first:
                first = False
            elif printed_nothing:
                print("")
            elif should_proceed:
                print("\n")
            should_proceed = False
            printed_nothing = False
        elif line and reading == 1:
            parts = line.split("\t")
            entities.append(parts[2])
            scores.append(parts[3])
        elif line and reading == 2:
            parts = line.split("\t")
            golds.append(parts[0])
        elif not line and reading == 2:
            optimal, suboptimal = process_gathered_entities()

            printed_nothing = len(optimal) == 0 and len(suboptimal) == 0

            entities = []
            golds = []
            scores = []
            should_proceed = True

        if not line:
            reading = (reading + 1) % 3

if len(entities) > 0:
    process_gathered_entities()

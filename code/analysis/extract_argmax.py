import argparse

parser = argparse.ArgumentParser(description='Create a relation prediction file from scores and reference relations.')
parser.add_argument('--score_file')
parser.add_argument('--relation_file')
args = parser.parse_args()


first = True

pred_file = open(args.score_file, 'r')
rel_file = open(args.relation_file, 'r')

curr_best = None
curr_best_score = None

first = True

line = 0
for pred, rel in zip(pred_file, rel_file):
    pred = pred.strip()
    rel = rel.strip()

    if (not pred and rel) or (not rel and pred):
        print("\nERROR: Mismatched files at line " + str(line))
        exit()
    if pred:
        score = float(pred)
        if curr_best_score is None or score > curr_best_score:
            curr_best_score = score
            curr_best = rel
    else:
        if first:
            first = False
        else:
            print("")

        if curr_best is not None:
            rel_parts = curr_best.strip().split("\t")
            print("\t".join([rel_parts[0], rel_parts[2], rel_parts[3], rel_parts[4]]), end="")

        curr_best = None
        curr_best_score = None

    line += 1
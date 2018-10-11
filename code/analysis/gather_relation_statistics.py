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

output_dict = {}
rel_dict = {}

line = 0
for pred, rel in zip(pred_file, rel_file):
    pred = pred.strip()
    rel = rel.strip()

    if (not pred and rel) or (not rel and pred):
        print("\nERROR: Mismatched files at line " + str(line))
        exit()
    if pred:
        score = float(pred)
        n_rel = rel.strip().split("\t")
        is_gold = n_rel[4] == "True"
        n_rel = [n_rel[0], n_rel[2], n_rel[3]]

        if curr_best_score is None or score > curr_best_score:
            curr_best_score = score
            curr_best = ["\t".join(n_rel)]
        elif curr_best_score == score:
            curr_best.append("\t".join(n_rel))

        rel_dict["\t".join(n_rel)] = [score, is_gold]

    else:
        for rel, info in rel_dict.items():
            rel_key = "->".join(rel.split("\t")[1:])
            if info[1] or rel in curr_best:
                if rel_key not in output_dict:
                    output_dict[rel_key] = [0, 0, 0, {}]

            if info[1] and rel in curr_best:
                output_dict[rel_key][0] += 1
            if rel in curr_best:
                output_dict[rel_key][1] += 1
            if info[1]:
                output_dict[rel_key][2] += 1

            if info[1] and not rel in curr_best:
                prev_confusion_dict = output_dict[rel_key][3]
                for r in curr_best:
                    r_key = "->".join(r.split("\t")[1:])
                    if r_key not in prev_confusion_dict:
                        prev_confusion_dict[r_key] = 1
                    else:
                        prev_confusion_dict[r_key] += 1

        curr_best = None
        curr_best_score = None
        rel_dict = {}

    line += 1

for key in output_dict:
    mfc = None
    mfc_count = 0
    for r, c in output_dict[key][3].items():
        if c > mfc_count:
            mfc = r
            mfc_count = c

    out_str = mfc + "==" + str(mfc_count) if mfc else ""

    output_dict[key][3] = out_str

for key, value in output_dict.items():
    output = "\t".join([key] + [str(x) for x in value])
    print(output)
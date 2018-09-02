import argparse

parser = argparse.ArgumentParser(description='Evaluate predictions against gold.')
parser.add_argument('--predictions')
parser.add_argument('--gold')
args = parser.parse_args()

pred_file = open(args.predictions, "r")
gold_file = open(args.gold, "r")


def compute_p_r_f1(predictions, targets):
    target = set(targets)
    predictions = set(predictions)

    tp = len(target & predictions)
    fp = len(predictions) - tp
    fn = len(target) - tp

    if tp > 0:
        precision = float(tp) / (tp + fp)
        recall = float(tp) / (tp + fn)

        return precision, recall, 2 * ((precision * recall) / (precision + recall))
    else:
        return 1.0, 0.0, 0.0

counter = 0
sum_p = 0
sum_r = 0
sum_f1 = 0
for pred_line, gold_line in zip(pred_file, gold_file):
    counter += 1
    preds = pred_line.strip().split(",")
    golds = gold_line.strip().split(",")

    if len(preds) == 1 and preds[0] == "":
        preds = []

    p, r, f1 = compute_p_r_f1(preds, golds)

    sum_p += p
    sum_r += r
    sum_f1 += f1

final_p = sum_p / counter
final_r = sum_r / counter
final_f1 = sum_f1 / counter

print("Precision: " + str(final_p))
print("Recall: " + str(final_r))
print("F1: " + str(final_f1))
import argparse
import random

from code.auxilliaries.virtuoso_graph_reader import VirtuosoGraphReader

parser = argparse.ArgumentParser(description='Evaluate predictions against gold.')
parser.add_argument('--question_file')
parser.add_argument('--score_file')
parser.add_argument('--gold_file')
parser.add_argument('--relation_file')
parser.add_argument('--annotation_file')
parser.add_argument('--relation_count_file')
args = parser.parse_args()

graph_reader = VirtuosoGraphReader()

sentences = []
sentence = []

golds = []

train_count_dict = {}
with open(args.relation_count_file, 'r') as r_file:
    for line in r_file:
        line = line.strip()
        if line:
            parts = line.split("\t")
            rel = parts[0] + "\t" + parts[1]
            count = int(parts[2])

            train_count_dict[rel] = count

with open(args.question_file, 'r') as i_file:
    for line in i_file:
        line = line.strip()
        if line:
            sentence.append(line.split("\t")[1])
        else:
            sentences.append(" ".join(sentence))
            sentence = []

with open(args.gold_file, 'r') as g_file:
    for line in g_file:
        line = line.strip()
        golds.append(line)

pred_file = open(args.score_file, 'r')
rel_file = open(args.relation_file, 'r')

curr_best = []
curr_best_score = None

true_outputs = []

line = 0
q_pointer = 0

items = [None] * len(sentences)

def format_rel(rel, score):
    parts = rel.strip().split("\t")

    r = parts[2] + "\t" + parts[3]
    count = train_count_dict[r] if r in train_count_dict else 0

    out_parts = parts[:4] + [str(score), str(count)]

    return "\t".join(out_parts)


for pred, rel in zip(pred_file, rel_file):
    pred = pred.strip()
    rel = rel.strip()

    if (not pred and rel) or (not rel and pred):
        print("\nERROR: Mismatched files at line " + str(line))
        exit()
    if pred:
        score = float(pred)
        rel_parts = rel.strip().split("\t")

        if rel_parts[4] == "True":
            true_outputs.append(format_rel(rel, score))

        if curr_best_score is None or score > curr_best_score:
            curr_best_score = score
            curr_best = [format_rel(rel, score)]
        elif curr_best_score == score:
            curr_best.append(format_rel(rel, score))
    else:
        print("Preprocessing question #"+str(q_pointer), end="\r")
        question = sentences[q_pointer]
        is_error = False
        for pred in curr_best:
            if pred not in true_outputs:
                is_error = True

        items[q_pointer] = [question, curr_best, true_outputs, is_error, golds[q_pointer]]

        curr_best = []
        curr_best_score = None
        true_outputs = []
        q_pointer += 1

    line += 1

print("")
random.shuffle(items)

annotation_file = open(args.annotation_file, "w")

def double_print(line):
    print(line)
    print(line, file=annotation_file)

def post_format(rel):
    parts = rel.strip().split("\t")

    entity = parts[0]
    rel1 = parts[2]
    rel2 = parts[3]

    predicted_entity = list(set(graph_reader.query(entity, rel1, rel2)))

    if len(predicted_entity) > 10:
        pent = " | ".join(predicted_entity[:10]) + " | [ and " + str(len(predicted_entity)-10) + " more. ]"
    else:
        pent = " | ".join(predicted_entity)

    parts.append(pent)
    return "\t".join(parts)

counter = 1
for item in items:
    if not item[3]:
        continue
    else:
        double_print("Question " + str(counter) + ":\n" + item[0] + "\n")

        double_print("Predictions:")
        for p in item[1]:
            double_print(post_format(p))
        double_print("")

        double_print("True hyperpaths:")
        for g in item[2]:
            double_print(post_format(g))

        double_print("")

        double_print("Gold entities:")
        double_print(item[4])

        annotation = input("\nChoose annotation for example: ")
        print("", file=annotation_file)
        print("Error type: ", file=annotation_file)
        print(annotation, file=annotation_file)

        if counter == 100:
            break
        else:
            double_print("\n")
            counter += 1

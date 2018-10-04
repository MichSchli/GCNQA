import argparse
import json
import sys

parser = argparse.ArgumentParser(description='Remove all relations not occuring at least min_n times as positives.')
parser.add_argument('--json_file')
args = parser.parse_args()

items = []

for line in open(args.json_file, 'r'):
    line = line.strip()
    if line:
        json_line = json.loads(line)
        question = json_line["question"]
        entities = [e["kb_id"][4:-1] for e in json_line["entities"]]
        answers = [a["text"] if a["text"] is not None else a["kb_id"] for a in json_line["answers"]]

        items.append((question, entities, answers))

first = True
for item in items:
    if first:
        first = False
    else:
        print("")

    question_split = item[0].split(" ")
    for i,word in enumerate(question_split):
        out = ["_"] * 6
        out[0] = str(i)
        out[1] = word
        print("\t".join(out))

    print("")

    entities = item[1]
    for entity in entities:
        out = ["_"]*5
        out[2] = entity
        out[3] = "0"
        print("\t".join(out))

    print("")

    answers = item[2]
    for answer in answers:
        if answer.strip():
            out = ["_"]*2
            out[1] = answer
            print("\t".join(out))
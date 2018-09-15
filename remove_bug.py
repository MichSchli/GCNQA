f = "data/webquestions/train/all_relations.txt"

skipping = False
for line in open(f):
    line = line.strip()

    if line.startswith("m."):
        skipping = False
    elif line.startswith("Query"):
        skipping = True

    if not skipping:
        print(line)
import argparse
from operator import itemgetter

parser = argparse.ArgumentParser(description='Sort and count the gold relations in a file.')
parser.add_argument('--input_file')
args = parser.parse_args()

observations = {}

for line in open(args.input_file, 'r'):
    line = line.strip()
    if line:
        parts = line.split("\t")
        if parts[4] == "True":
            relation = parts[2] + "\t" + parts[3]

            if relation not in observations:
                observations[relation] = 1
            else:
                observations[relation] += 1

sorted_golds = sorted(observations.items(), key=itemgetter(1), reverse=True)
for rel, freq in sorted_golds:
    print(rel + "\t" + str(freq))
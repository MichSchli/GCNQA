import argparse
from operator import itemgetter

parser = argparse.ArgumentParser(description='Remove all relations not occuring at least min_n times as positives.')
parser.add_argument('--input_file')
parser.add_argument('--gold_count_file')
parser.add_argument('--min_n')
args = parser.parse_args()

observations = {}

min_n = int(args.min_n)

for line in open(args.gold_count_file, 'r'):
    line = line.strip().split("\t")
    rel = line[0] + "\t" + line[1]
    count = int(line[2])

    observations[rel] = count

for line in open(args.input_file, 'r'):
    line = line.strip()
    if line:
        parts = line.split("\t")
        relation = parts[2] + "\t" + parts[3]

        if relation in observations and observations[relation] >= min_n:
            print("\t".join(parts))
    else:
        print("")
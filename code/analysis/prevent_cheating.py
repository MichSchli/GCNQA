import argparse
import random
from operator import itemgetter

parser = argparse.ArgumentParser(description='Make sure models cannot cheat regardless of implementation bugs.')
parser.add_argument('--input_file')
args = parser.parse_args()

answered = False
count_answered = 0
count_total = 1

out = []
for line in open(args.input_file, 'r'):
    line = line.strip()
    if line:
        parts = line.split("\t")
        parts[4] = "_"
        out.append("\t".join(parts))
    else:
        out = out
        random.shuffle(out)
        print("\n".join(out))
        if len(out) > 0:
            print("")
        out = []

if len(out) > 0:
    out = out
    random.shuffle(out)
    print("\n".join(out))
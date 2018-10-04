import argparse
from operator import itemgetter

parser = argparse.ArgumentParser(description='Remove all relations not occuring at least min_n times as positives.')
parser.add_argument('--file_1')
parser.add_argument('--file_2')
args = parser.parse_args()

items = [[]]

for line in open(args.file_1, 'r'):
    line = line.strip()
    if line:
        items[-1].append(line)
    else:
        items.append([])

if not items[-1]:
    items = items[:-1]

items.append([])

for line in open(args.file_2, 'r'):
    line = line.strip()
    if line:
        items[-1].append(line)
    else:
        items.append([])

if not items[-1]:
    items = items[:-1]

items = ["\n".join(lines) for lines in items]

first = True

for item in items:
    if first:
        first = False
    else:
        print("")
        if item:
            print("")

    print(item, end="")
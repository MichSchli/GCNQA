import argparse
import random

parser = argparse.ArgumentParser(description='Remove all relations not occuring at least min_n times as positives.')
parser.add_argument('--in_file')
parser.add_argument('--file_1')
parser.add_argument('--file_2')
parser.add_argument('--second_file_size')
args = parser.parse_args()

items = []

for line in open(args.in_file, 'r'):
    line = line.strip()
    if line:
        items.append(line)

split_idx = int(args.second_file_size)
first_file_items = items[:-split_idx]
second_file_items = items[-split_idx:]

with open(args.file_1, "w") as outfile:
    first = True
    for item in first_file_items:
        if first:
            first = False
        else:
            print("", file=outfile)

        print(item, end="", file=outfile)


with open(args.file_2, "w") as outfile:
    first = True
    for item in second_file_items:
        if first:
            first = False
        else:
            print("", file=outfile)

        print(item, end="", file=outfile)
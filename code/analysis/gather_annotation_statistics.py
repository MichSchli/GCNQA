import argparse
import operator
import random
from operator import itemgetter

parser = argparse.ArgumentParser(description='Make sure models cannot cheat regardless of implementation bugs.')
parser.add_argument('--annotation_file')
args = parser.parse_args()

type_dict = {}

type_next = False

for line in open(args.annotation_file, 'r'):
    line = line.strip()

    if line == "Error type:":
        type_next = True
    elif type_next:
        type_next = False

        listed_types = line.split("|")

        for listed_type in listed_types:
            if listed_type not in type_dict:
                type_dict[listed_type] = 1
            else:
                type_dict[listed_type] += 1

sorted_dict = reversed(sorted(type_dict.items(), key=operator.itemgetter(1)))

for type, count in sorted_dict:
    spacing = " " * (60 - len(type))
    print(type + spacing + str(count))
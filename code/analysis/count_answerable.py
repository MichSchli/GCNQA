import argparse
from operator import itemgetter

parser = argparse.ArgumentParser(description='Sort and count the gold relations in a file.')
parser.add_argument('--input_file')
args = parser.parse_args()

answered = False
count_answered = 0
count_total = 1

for line in open(args.input_file, 'r'):
    line = line.strip()
    if line:
        parts = line.split("\t")
        if parts[4] == "True" and not answered:
            count_answered += 1
            answered = True
    else:
        answered = False
        count_total += 1

print("Can answer:\t" + str(count_answered))
print("Total:\t" + str(count_total))
print("Answerability:\t" + str(count_answered/count_total))
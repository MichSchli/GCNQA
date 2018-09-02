import argparse

parser = argparse.ArgumentParser(description='Extract gold relations from a conll file.')
parser.add_argument('--input_file')
args = parser.parse_args()

reading = 0
entities = []
sentence = []
with open(args.input_file, 'r') as i_file:
    for line in i_file:
        line = line.strip()
        if line and reading == 0:
            sentence.append(line)
        elif line and reading == 1:
            parts = line.split("\t")
            entities.append(parts[2])

        if not line and (reading == 0 or reading == 1):
            reading += 1
        elif not line:
            reading = 0
            print("\n".join(sentence))
            print("")

            entities = []
            sentence = []

if len(entities) > 0:
    print("\n".join(sentence), end="")
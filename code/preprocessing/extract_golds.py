import argparse

parser = argparse.ArgumentParser(description='Extract gold entities conll file.')
parser.add_argument('--input_file')
args = parser.parse_args()

reading = 0
golds = []
sentences = []
with open(args.input_file, 'r') as i_file:
    for line in i_file:
        line = line.strip()
        if line and reading == 0:
            sentences.append(line)
        elif line and reading == 2:
            parts = line.split("\t")
            golds.append(parts[1])

        if not line and (reading == 0 or reading == 1):
            reading += 1
        elif not line:
            reading = 0
            print(",".join(golds))

            golds = []
            sentences = []

if len(sentences) > 0:
    print("\n".join(golds), end="")
from Mindblocks.interface import BasicInterface

interface = BasicInterface()

block_filepath = "blocks/pure_relation_prediction.block"
embedding_filepath = "data/glove.6B/glove.6B.100d.txt"
data_filepath = "data/toy-125"
interface.load_file(block_filepath)
interface.set_variable("embedding_filepath", embedding_filepath)
interface.set_variable("data_folder", data_filepath)
interface.initialize()

interface.train()
interface.validate()

first = True
with open("output.txt", 'w') as output_file:
    for line in interface.predict():
        if first:
            first = False
        else:
            print("", file=output_file)
        if line is not None:
            print("\t".join([line[0], line[2], line[3]]), file=output_file, end="")
        else:
            print(line, file=output_file, end="")
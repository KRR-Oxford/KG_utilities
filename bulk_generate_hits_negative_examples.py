from argparse import ArgumentParser
from random import randint
import os
import divide
import generate_hits_negative_examples

# Read the argument from command line
parser = ArgumentParser()
parser.add_argument('--root', help="Folder where all dataset folders are.")
parser.add_argument('--num-examples',help = "Number of negative examples per positive")
parser.add_argument('--name-output', help = "Name of the folder where the examples are generated")
args = parser.parse_args()

assert os.path.exists(args.root)

# Read the corresponding files
for folder in [x[0] for x in os.walk(args.root)]:
    graph_file = folder + '/test/test-graph.txt' 
    positive_examples_file = folder +'/test/test-fact.txt' 
    if os.path.exists(graph_file) and os.path.exists(positive_examples_file): 
        print("Generating examples for {}".format(folder)) 
        generate_hits_negative_examples.generate_negative_examples(graph_file,positive_examples_file,args.num_examples,args.name_output)


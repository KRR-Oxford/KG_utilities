from argparse import ArgumentParser
from random import randint
import os
import filter_positive_examples 


# Read the argument from command line 
parser = ArgumentParser()
parser.add_argument("input", help="Root folder with all datasets.")
args = parser.parse_args()

# Ensure that input is a valid folder
assert os.path.exists(args.input)

# Read the corresponding files
for folder in [x[0] for x in os.walk(args.input)]:
    graph_file = folder + '/test/test-graph.txt' 
    facts_file = folder + '/test/test-fact.txt' 
    if os.path.exists(graph_file) and os.path.exists(facts_file): 
        filter_positive_examples.filter(graph_file,facts_file)
        print("Filtered facts in file " + facts_file) 


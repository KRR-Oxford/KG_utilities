from argparse import ArgumentParser
from random import randint
import os
import divide_nodepreserving


# Read the argument from command line 
parser = ArgumentParser()
parser.add_argument('--input', help="Root folder with all datasets.")
parser.add_argument('--file', help="String of the file within the dataset folder e.g. /test/test.txt")
parser.add_argument('--ratio', help="Maximum ratio of dataset to positive examples size." )
args = parser.parse_args()

# Ensure that input is a valid folder
assert os.path.exists(args.input)

# Read the corresponding files
for folder in [x[0] for x in os.walk(args.input)]:
    target_file = folder + args.file 
    if os.path.exists(target_file): 
        print("Dividing facts in {}".format(target_file))
        divide_nodepreserving.split_1_to_k(target_file,args.ratio)
        print("Done")


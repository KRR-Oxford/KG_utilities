from argparse import ArgumentParser
from random import randint
import os
import divide

'''This method applies divide to the whole dataset, to a file called test.txt
in a 'test' folder. '''

# Read the argument from command line 
parser = ArgumentParser()
parser.add_argument("input")
parser.add_argument("X")
args = parser.parse_args()

# Ensure that input is a valid folder
assert os.path.exists(args.input)

# Read the corresponding files
for folder in [x[0] for x in os.walk(args.input + 'MeGaNN/data/')]:
    target_file = folder + '/train/train.txt' 
    if os.path.exists(target_file): 
        divide.split_1_to_k(target_file,args.X)
        print("Divided facts in file " + target_file) 


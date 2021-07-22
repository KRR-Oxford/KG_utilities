from argparse import ArgumentParser
from os.path import splitext

# Read the argument from command line
parser = ArgumentParser()
parser.add_argument("input")
args = parser.parse_args()

# Read the corresponding file
inputFile = open(args.input, "r")
Lines = inputFile.readlines()

# Get file name and extension
fname, fext = splitext(args.input)

# Define output file
outputFile = open(fname + "_constants.csv", "w")

#Initialise set of predicates
constants = set() 

for line in Lines:
    # Mine the three entities.
    ent1, ent2, ent3 = line.split(None,3)
    if ent3.endswith('\n'):
        ent3 = ent3[:-1]
    # Check that predicate has not been seen already, otherwise do nothing.
    if ent1 not in constants:
        # Add to set 
        constants.add(ent1)
        # Write new string 
        outputFile.write(ent1 + "\n")
    if ent3 not in constants:
        # Add to set 
        constants.add(ent3) 
        # Write new string 
        outputFile.write(ent3 + "\n")


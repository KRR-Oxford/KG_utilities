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

#Initialise set of predicates
predicates = set() 
#Initialise set of constants 
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
    if ent3 not in constants:
        # Add to set 
        constants.add(ent3) 
    if ent2 not in predicates:
        # Add to set 
        predicates.add(ent2) 

print("Total number of constants: {}".format(len(constants)))
print("Total number of predicates: {}".format(len(predicates)))
print("Total number of possible facts: {}".format(len(constants)*len(constants)*len(predicates)))


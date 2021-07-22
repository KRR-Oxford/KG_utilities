from argparse import ArgumentParser
from os.path import splitext

# Print warning
print("WARNING: This program only extracts binary predicates at the moment.") 

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
outputFile = open(fname + "_predicates.csv", "w")

#Initialise set of predicates
predicates = set() 

# Filter by extension
for line in Lines:
    # Mine the three entities.
    ent1, ent2, ent3 = line.split(None,2)
    # Check that predicate has not been seen already, otherwise do nothing.
    if ent2 not in predicates:
        # Add to set 
        predicates.add(ent2)
        # Write new string 
        outputFile.write(ent2 + "\n")


from argparse import ArgumentParser

# Read the argument from command line
parser = ArgumentParser()
parser.add_argument("input")
args = parser.parse_args()

# Read the corresponding file
inputFile = open(args.input, "r")
Lines = inputFile.readlines()

# Define output files
outputFile = open(args.input[:-3] + ".txt", "w")

for line in Lines:
    # Mine the three entities.
    ent1, ent2, ent3, ent4 = line.split(" ")
    # Remove end of line character from last entitiy 
    # Write new string 
    outputFile.write(ent1 + "\t" + ent2 + "\t" + ent3 + "\n")

outputFile.close

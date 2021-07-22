from argparse import ArgumentParser
import os
from os.path import splitext

def extract_predicates(file, dataset_name, predicates_folder):


    # Read the corresponding file
    inputFile = open(file, "r")
    Lines = inputFile.readlines()

    # Get file name and extension
    fname, fext = splitext(file)

    # Define output file
    output_file_name = predicates_folder + "/" + dataset_name + "_predicates.csv"
    outputFile = open(output_file_name, "w")

    #Initialise set of predicates
    unaryPredicates = set() 
    binaryPredicates = set()

    # Filter by extension
    for line in Lines:
        # Mine the three entities.
        ent1, ent2, ent3 = line.split(None,2)
        if ent2 == "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>" :
            # Remove end of line character. 
            if ent3.endswith('\n'):
                ent3 = ent3[:-1]
            # Check that predicate has not been seen already, otherwise do nothing.
            if ent3 not in unaryPredicates:
                unaryPredicates.add(ent3)
                outputFile.write(ent3 + ",1" + "\n")
        else :
            # Check that predicate has not been seen already, otherwise do nothing.
            if ent2 not in binaryPredicates:
                binaryPredicates.add(ent2)
                outputFile.write(ent2 + ",2" + "\n")

    return output_file_name 

if __name__ == '__main__':
    
    # Read the argument from command line
    parser = ArgumentParser()
    parser.add_argument("input")
    args = parser.parse_args()
    
    extract_predicates(args.input, os.path.basename(args.input), '.')







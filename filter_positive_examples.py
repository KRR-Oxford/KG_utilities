from argparse import ArgumentParser
from random import choice 
from os.path import splitext

'''This method takes a single 'input' file representing a set of triples,
and separates it into two files according to the proportion 1:X. '''

def filter(file_graph,file_facts):
  
    type_string = "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>" 

    # Read the corresponding file
    input_file_graph = open(file_graph, "r") 
   
    # First processing
    constants = set()
    pairs = set()

    for line in input_file_graph.readlines():
        ent1, ent2, ent3 = line.split()
        if ent3.endswith('\n'):
            ent3 = ent3[:-1]
        if ent2 == type_string:
            constants.add(ent1)
        else:
            pairs.add(frozenset((ent1,ent3)))
      

    input_file_facts = open(file_facts, "r")

    total_number_of_facts = 0

    usable_facts = set()

    for line in input_file_facts.readlines():
        total_number_of_facts += 1 
        ent1, ent2, ent3 = line.split()
        fact = (ent1,ent2,ent3) 
        if ent3.endswith('\n'):
            ent3 = ent3[:-1]
        if ent2 == type_string and ent1 in constants:
            usable_facts.add(fact)
        elif frozenset((ent1,ent3)) in pairs:
            usable_facts.add(fact)

    print("Usable facts: {} out of {}".format(len(usable_facts),total_number_of_facts))

    # Mine name and extension of original input file
    fname = splitext(file_facts)[0]
    fext = splitext(file_facts)[1]  
    output = open(fname + "_filtered" + fext, "w")

    #For each read line, roll the random variable, and write in the corresponding file.
    for (ent1,ent2,ent3) in usable_facts:
        output.write("{}\t{}\t{}\n".format(ent1,ent2,ent3))
 
    output.close


if __name__ == '__main__':

    # Read the argument from command line 
    parser = ArgumentParser()
    parser.add_argument('--test-graph', help= "Dataset with incompete graph.")
    parser.add_argument('--test-facts', help= "Dataset with positive examples.")
    args = parser.parse_args()
   
    # Execute split on read arguments
    filter(args.test_graph,args.test_facts)



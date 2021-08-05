from argparse import ArgumentParser
import random
import torch
from os.path import splitext

type_string = "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>" 


def list_to_inverse_dictionary(list):
    dictionary = {} 
    for i, elem in enumerate(list):
        dictionary[elem] = i
    return dictionary


def generate_negatives(file, positive_examples_file):
 
    # Compute number of negative examples needed 
    inputFile = open(positive_examples_file,'r')
    Lines = inputFile.readlines()
    target_number = len(Lines) 

    # Read the file with the complete graph
    inputFile = open(file, "r") 
    Lines = inputFile.readlines()

    # The problem with this program is that we cannot generate all negative examples and then pick a few of them;
    # that would probably occupy too much space. Instead, we create a tensor representing all possible facts,
    # and randomly guess positions of this tensor corresponding to facts not in the complete graph.

    # Process the complete graph into these four lists (with no duplicates). Also, store all facts in the complete graph.
    unary_predicates = [] 
    binary_predicates = [] 
    single_constants = [] 
    pairs_constants = [] 

    facts = set()

    for line in Lines:
        ent1, ent2, ent3 = line.split()
        if ent3.endswith('\n'):
            ent3 = ent3[:-1]
        if ent2 == type_string:
            if ent1 not in single_constants:
                single_constants.append(ent1)
            if ent3 not in unary_predicates:
                unary_predicates.append(ent3) 
            facts.add((ent1,ent2,ent3))
        else:
            if (ent1,ent3) not in pairs_constants: # Note that due to the way we add elements to the list, if (e1,e3) not there, then (e3,e1) not there either.
                pairs_constants.append((ent1,ent3))
                if ent1 != ent3:
                    pairs_constants.append((ent3,ent1)) 
            if ent2 not in binary_predicates:
                binary_predicates.append(ent2)
            facts.add((ent1,ent2,ent3))
          
    # Sanity check: no duplicates in the lists
    assert len(set(unary_predicates)) == len(unary_predicates)
    assert len(set(binary_predicates)) == len(binary_predicates)
    assert len(set(single_constants)) == len(single_constants)
    assert len(set(pairs_constants)) == len(pairs_constants)

    # Produce dictionaries by reversing the lists. This works because these lists have no duplicates.
    unary_predicate_to_int = list_to_inverse_dictionary(unary_predicates)
    binary_predicate_to_int = list_to_inverse_dictionary(binary_predicates)
    single_constant_to_int = list_to_inverse_dictionary(single_constants)
    pair_constants_to_int = list_to_inverse_dictionary(pairs_constants)
    
    # Initialise tensors corresponding to all possible facts represented in the encoding of the graph. 
    unary_tensor = torch.zeros(len(single_constants),len(unary_predicates)) 
    binary_tensor = torch.zeros(len(pairs_constants),len(binary_predicates))
    
    # Fill in tensors
    for (ent1,ent2,ent3) in facts:
        if ent2 == type_string:
            # Minus one because of the way indices work for tensors: the first row gets the index 0.
            row = single_constant_to_int[ent1]  
            column = unary_predicate_to_int[ent3] 
            unary_tensor[row,column] = 1
        else:
            row = pair_constants_to_int[(ent1,ent3)] 
            column = binary_predicate_to_int[ent2] 
            binary_tensor[row,column] = 1 

    # Count tensor components that are zero
    zero_positions_counter = 0 
    for row in range(len(single_constants)):
        for column in range(len(unary_predicates)):
            if unary_tensor[row,column] == 0:
                zero_positions_counter += 1 
    for row in range(len(pairs_constants)):
        for column in range(len(binary_predicates)):
            if binary_tensor[row,column] == 0:
                zero_positions_counter += 1

    # Initialise set of negative examples 
    negative_examples = set()
    number_of_negative_examples = min(zero_positions_counter,target_number)
    if number_of_negative_examples != target_number:
        print("WARNING: Not enough negative examples can be created.")
        print("We have {} positive examples, but can only create up to {} negative examples".format(target_number,zero_positions_counter))
   
    # Choose which negative examples are selected by randomly selecting their ordinals among all examples with zeroes.
    targets = random.sample(range(0,zero_positions_counter),number_of_negative_examples)

    # Harvest negative examples; count again zeroes in tensor, and if the counter is equal to a target number, select example.
    zero_positions_counter = 0 
    for row in range(len(single_constants)):
        for column in range(len(unary_predicates)):
            if unary_tensor[row,column] == 0:
                if zero_positions_counter in targets:
                    negative_examples.add((unary_constants[row],type_string,unary_predicates[column]))
                zero_positions_counter += 1

    for row in range(len(pairs_constants)):
        for column in range(len(binary_predicates)):
            if binary_tensor[row,column] == 0:
                if zero_positions_counter in targets:
                    (c1,c3) = pairs_constants[row]
                    negative_examples.add((c1,binary_predicates[column],c3))
                zero_positions_counter += 1

    # Mine name and extension of original input file
    fname = splitext(file)[0]
    fext = splitext(file)[1]  

    # Define output files: two for training, and two for testing 
    output = open(fname + "_negative_examples" + fext, "w")

    #For each read line, roll the random variable, and write in the corresponding file.
    for (ent1,ent2,ent3) in negative_examples:
        output.write("{}\t{}\t{}\n".format(ent1,ent2,ent3))
 
    output.close


if __name__ == '__main__':

    # Read the argument from command line 
    parser = ArgumentParser()
    parser.add_argument('--complete_graph',help="File with the (complete) graph")
    parser.add_argument('--facts',help="File with the positive examples")
    args = parser.parse_args()
   
    # Execute split on read arguments
    generate_negatives(args.complete_graph,args.facts)



from argparse import ArgumentParser
from random import choice 
from os.path import splitext

'''This method takes a single 'input' file representing a set of triples,
and separates it into two files according to the proportion 1:X. '''

def split_1_to_k(file, number):
  
    type_string = "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>" 

    # Read the corresponding file
    inputFile = open(file, "r") 
    Lines = inputFile.readlines()

    # Consider separately facts 
    candidate_facts = set() 
    dataset_facts = set()
    positive_examples_facts = set()
    unary_facts_index = {}
    binary_facts_index = {}

    
    # First processing
    for line in Lines:
        ent1, ent2, ent3 = line.split()
        if ent3.endswith('\n'):
            ent3 = ent3[:-1]
        candidate_facts.add((ent1,ent2,ent3)) 
        if ent2 == type_string:
        # There must be a simpler, more idiomatic way of doing this, but I haven't found it 
            unary_facts_index[ent1] = unary_facts_index.get(ent1,set()) 
            unary_facts_index[ent1].add(ent3) 
        else:
            binary_facts_index[(ent1,ent3)] = binary_facts_index.get((ent1,ent3),set()) 
            binary_facts_index[(ent1,ent3)].add(ent2) 
      
    number_total_facts = len(candidate_facts)
    print("Total number of facts: {}".format(len(candidate_facts)))

    # Facts that cannot become positive examples are passed on to the dataset dataset
    silly_copy = unary_facts_index.copy() 
    for key in silly_copy:
        if len(unary_facts_index[key]) == 1:
            # Note that this deletes the key from the dictionary. Second pop opens the set. 
            fact = (key,type_string,unary_facts_index.pop(key).pop())
            dataset_facts.add(fact)
            candidate_facts.remove(fact)
            
    silly_copy = binary_facts_index.copy() 
    for (key1,key2) in silly_copy: 
        if len(binary_facts_index[(key1,key2)]) == 1 and key1 != key2 and (key2,key1) not in binary_facts_index:
            fact = (key1,binary_facts_index.pop((key1,key2)).pop(),key2)
            dataset_facts.add(fact)
            candidate_facts.remove(fact)
        elif len(binary_facts_index[(key1,key2)]) == 1 and key1 == key2:
            fact = (key1,binary_facts_index.pop((key1,key2)).pop(),key2)
            dataset_facts.add(fact)
            candidate_facts.remove(fact)



  #  print("Remaining number of facts: {}".format(len(candidate_facts)))
  
    #INVARIANT: for binary facts, we ensure that in the candidate set, if there is only one fact for a,b, then there is at least one for b,a.
    # Main loop
    while candidate_facts and len(positive_examples_facts)/(len(dataset_facts)+len(candidate_facts)) < 1/int(number):
        fact = choice(tuple(candidate_facts))
        (ent1,ent2,ent3) = fact 
        
        positive_examples_facts.add(fact) 
        candidate_facts.remove(fact)

        if ent2 == type_string:
            # Remove from index 
            unary_facts_index[ent1].remove(ent3)     
            # If entry for this constant has only one value left, remove it and add it to dataset dataset 
            if len(unary_facts_index[ent1]) == 1:
                fact2 = (ent1,type_string,unary_facts_index.pop(ent1).pop())
                dataset_facts.add(fact2)
                candidate_facts.remove(fact2)
        else:
            binary_facts_index[(ent1,ent3)].remove(ent2)
            # Check if there is one left 
            if (ent1,ent3) in binary_facts_index:
                if len(binary_facts_index[(ent1,ent3)]) == 1 and ent1 != ent3 and (ent3,ent1) not in binary_facts_index:
                    fact2 = (ent1,binary_facts_index.pop((ent1,ent3)).pop(),ent3)
                    dataset_facts.add(fact2)
                    candidate_facts.remove(fact2)
                elif len(binary_facts_index[(ent1,ent3)]) == 1 and ent1 == ent3 :
                    fact2 = (ent1,binary_facts_index.pop((ent1,ent3)).pop(),ent3)
                    dataset_facts.add(fact2)
                    candidate_facts.remove(fact2)
            #Otherwise, the mirror pair must have at least one element. 
            elif len(binary_facts_index[(ent3,ent1)]) == 1:
                fact2 = (ent3,binary_facts_index.pop((ent3,ent1)).pop(),ent1)
                dataset_facts.add(fact2)
                candidate_facts.remove(fact2)


    for fact in candidate_facts:
        dataset_facts.add(fact)
    
    assert len(dataset_facts) + len(positive_examples_facts) == number_total_facts
    print("From {} facts, made a dataset with {} facts and {} positive examples".format(number_total_facts,len(dataset_facts),len(positive_examples_facts)))
    print("The proportion is {}".format(len(dataset_facts)/len(positive_examples_facts)))

    # Mine name and extension of original input file
    fname = splitext(file)[0]
    fext = splitext(file)[1]  

    # Define output files: two for training, and two for testing 
    smallOutput = open(fname + "_facts" + fext, "w")
    bigOutput = open(fname + "_graph" + fext, "w")


    #For each read line, roll the random variable, and write in the corresponding file.
    for (ent1,ent2,ent3) in dataset_facts:
        bigOutput.write("{}\t{}\t{}\n".format(ent1,ent2,ent3))
 
    for (ent1,ent2,ent3) in positive_examples_facts:
        smallOutput.write("{}\t{}\t{}\n".format(ent1,ent2,ent3))

    smallOutput.close
    bigOutput.close


if __name__ == '__main__':

    # Read the argument from command line 
    parser = ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("X")
    args = parser.parse_args()
   
    # Execute split on read arguments
    split_1_to_k(args.input,args.X)



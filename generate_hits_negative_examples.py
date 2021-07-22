from argparse import ArgumentParser
from os.path import splitext
import random
import os

def generate_negative_examples(incomplete_graph_file, positive_examples_file, neg_examples_per_positive, output):

    number_of_negative_examples_per_positive = int(neg_examples_per_positive)
        
    # Read and store the positive facts, while also getting a list of all constants,
    # relations, and classes. RDF:type is not counted as a relation, and any filler of
    # it is counted as a class.
    true_known_facts = set()
    positive_examples = set()
    constants = set()
    relations = set()
    classes = set()
    for line in open(positive_examples_file, "r").readlines():
        ent1, ent2, ent3 = line.split()
        if ent3.endswith('\n'):
            ent3 = ent3[:-1]
        read_triple = (ent1, ent2, ent3)
        if read_triple not in positive_examples:
            positive_examples.add(read_triple)
            true_known_facts.add(read_triple)
        if ent1 not in constants:
            constants.add(ent1)
        if ent2 == "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>":
            classes.add(ent3)
        else:
            constants.add(ent1)
            relations.add(ent2)
    #  This is as above, but we don't add tacts to the set of positive examples.
    for line in open(incomplete_graph_file, "r").readlines():
        ent1, ent2, ent3 = line.split()
        if ent3.endswith('\n'):
            ent3 = ent3[:-1]
        read_triple = (ent1, ent2, ent3)
        if read_triple not in positive_examples:
            true_known_facts.add(read_triple)
        if ent1 not in constants:
            constants.add(ent1)
        if ent2 == "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>":
            classes.add(ent3)
        else:
            constants.add(ent1)
            relations.add(ent2)


    #  Compute negative examples for the head
    negative_examples_heads = set()
    #  Produce the negative examples for each fact. 
    for fact in positive_examples:
        (head, body, tail) = fact
        #  Compute a set of all constants that might work as negative examples.
        candidate_replacement_constants = set() 
        for constant in constants:
            candidate_fact = (constant, body, tail)
            if candidate_fact not in true_known_facts:
                candidate_replacement_constants.add(constant)
        if len(candidate_replacement_constants) == 0:
            print("WARNING! I cannot add head negative examples for {} because"
                  " all corruptions of it are already positive examples".format(fact))
        #  Count number of negative examples: ideally 50, but less if we don't have enough constants
        number_of_negative_examples_for_this_fact = min(number_of_negative_examples_per_positive, len(candidate_replacement_constants))
        if (number_of_negative_examples_for_this_fact < number_of_negative_examples_per_positive):
            print("Warning: less than {} head examples generated for fact {} {} {}".format(neg_examples_per_positive,head,body,tail))
        #  Sample the corresponding number of constants from the list
        selected_replacement_constants = random.sample(candidate_replacement_constants,
                                                       k=number_of_negative_examples_for_this_fact)
        for constant in selected_replacement_constants:
            negative_examples_heads.add((constant, body, tail))

    #  Compute negative examples for the relation 
    negative_examples_bodies = set()
    #  Produce the negative examples for each fact. 
    for fact in positive_examples:
        (head, body, tail) = fact
        #  No replacements of the relation are done if the body is a type.  
        if body != "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>":
            #  Consider all constants that might work as negative examples. 
            candidate_replacement_relations = set() 
            for relation in relations:
                candidate_fact = (head, relation, tail)
                if candidate_fact not in true_known_facts:
                    candidate_replacement_relations.add(relation)
            if len(candidate_replacement_relations) == 0:
                print("WARNING! I cannot add relation negative examples for {} because"
                      " all corruptions of it are already positive examples".format(fact))
            #  Count number of negative examples: ideally 50, but less if we don't have enough relations 
            number_of_negative_examples_for_this_fact = min(number_of_negative_examples_per_positive, len(candidate_replacement_relations))
            if (number_of_negative_examples_for_this_fact < number_of_negative_examples_per_positive):
                print("Warning: less than {} body examples generated for fact {} {} {}".format(neg_examples_per_positive,head,body,tail))
            #  Sample the corresponding number of relations from the list
            selected_replacement_relations = random.sample(candidate_replacement_relations,
                                                           k=number_of_negative_examples_for_this_fact)
            for relation in selected_replacement_relations:
                negative_examples_bodies.add((head, relation, tail))


    negative_examples_tails = set()
    #  Produce the negative examples for each fact. 
    for fact in positive_examples:
        (head, body, tail) = fact
        #  IMPORTANT: If the body is RDF:type, we consider only other classes as possible replacements.
        #  If the body is another relation, we consider other constants as replacements 
        if body == "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>":
            candidate_replacement_classes = set() 
            for klass in classes:
                candidate_fact = (head, body, klass)
                if candidate_fact not in true_known_facts:
                    candidate_replacement_classes.add(klass)
            if len(candidate_replacement_classes) == 0:
                print("WARNING! I cannot add tail negative examples for {} because"
                      " all corruptions of it are already positive examples".format(fact))
            #  Count number of negative examples: ideally 50, but less if we don't have enough classes 
            number_of_negative_examples_for_this_fact = min(number_of_negative_examples_per_positive, len(candidate_replacement_classes)) 
            if (number_of_negative_examples_for_this_fact < number_of_negative_examples_per_positive):
                print("Warning: less than {} tail examples generated for fact {} {} {}".format(neg_examples_per_positive,head,body,tail))
            #  Sample the corresponding number of constants from the list
            selected_replacement_classes = random.sample(candidate_replacement_classes,
                                                         k=number_of_negative_examples_for_this_fact)
            for klass in selected_replacement_classes:
                negative_examples_tails.add((head, body, klass))
        else:
            candidate_replacement_constants = set() 
            for constant in constants:
                candidate_fact = (head, body, constant)
                if candidate_fact not in true_known_facts:
                    candidate_replacement_constants.add(constant)
            if len(candidate_replacement_constants) == 0:
                print("WARNING! I cannot add tail negative examples for {} because"
                      " all corruptions of it are already positive examples".format(fact))
            #  Count number of negative examples: ideally 50, but less if we don't have enough constants
            number_of_negative_examples_for_this_fact = min(number_of_negative_examples_per_positive, len(candidate_replacement_constants)) 
            if (number_of_negative_examples_for_this_fact < number_of_negative_examples_per_positive):
                print("Warning: less than {} tail examples generated for fact {} {} {}".format(neg_examples_per_positive,head,body,tail))
            #  Sample the corresponding number of constants from the list
            selected_replacement_constants = random.sample(candidate_replacement_constants,
                                                           k=number_of_negative_examples_for_this_fact)
            for constant in selected_replacement_constants:
                negative_examples_tails.add((head, body, constant))

    fname, fext = splitext(positive_examples_file)
    print("Original number of positive examples is {}".format(len(positive_examples)))
    #  Print to output file
    parent_folder = os.path.dirname(os.path.abspath(positive_examples_file)) + '/' + output
    if not os.path.exists(parent_folder):
        os.makedirs(parent_folder)
    output_file_all = open(parent_folder + "/all_with_positives" + fext, "w") 
    for fact in positive_examples:
        (ent1, ent2, ent3) = fact
        output_file_all.write(ent1 + '\t' + ent2 + '\t' + ent3 + '\n')
    output_file_heads = open(parent_folder + "/heads" + fext, "w") 
    for fact in negative_examples_heads:
        (ent1, ent2, ent3) = fact
        output_file_heads.write(ent1 + '\t' + ent2 + '\t' + ent3 + '\n')
        output_file_all.write(ent1 + '\t' + ent2 + '\t' + ent3 + '\n')
    print("Added {} head negative examples".format(len(negative_examples_heads)))
    output_file_heads.close()
    #  Print to output file
    output_file_bodies = open(parent_folder + "/bodies" + fext, "w") 
    for fact in negative_examples_bodies:
        (ent1, ent2, ent3) = fact
        output_file_bodies.write(ent1 + '\t' + ent2 + '\t' + ent3 + '\n')
        output_file_all.write(ent1 + '\t' + ent2 + '\t' + ent3 + '\n')
    print("Added {} body negative examples".format(len(negative_examples_bodies)))
    output_file_bodies.close()
    #  Print to output file
    output_file_tails = open(parent_folder + "/tails" + fext, "w") 
    for fact in negative_examples_tails:
        (ent1, ent2, ent3) = fact
        output_file_tails.write(ent1 + '\t' + ent2 + '\t' + ent3 + '\n')
        output_file_all.write(ent1 + '\t' + ent2 + '\t' + ent3 + '\n')
    print("Added {} tail negative examples".format(len(negative_examples_tails)))
    output_file_tails.close()
    output_file_all.close()

    
# Read the argument from command line

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--positive-examples',
            help='Name of the file with the positive examples')
    parser.add_argument('--incomplete-graph',
            help='Name of the file with the original incomplete graph')
    parser.add_argument('--num-examples',help = "Number of negative examples per positive")
    parser.add_argument('--name-output', help = "Name of the folder where the examples are generated")
    args = parser.parse_args()
    generate_negative_examples(args.incomplete_graph,args.positive_examples,args.num_examples,args.name_output)


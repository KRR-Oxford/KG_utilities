from argparse import ArgumentParser
from os.path import splitext
import random
import sys


#  This auxiliary method extracts the facts (without duplicates) from a file of triples 
def parse_facts(file):
    facts_to_output = set() 
    for line in open(file, "r").readlines():
        ent1, ent2, ent3 = line.split()
        if ent3.endswith('\n'):
            ent3 = ent3[:-1]
        read_triple = (ent1, ent2, ent3)
        if read_triple not in facts_to_output:
            facts_to_output.add(read_triple)
    return facts_to_output

#  Check if there is a match for the first k elements, with k the rank threshold 
def check_for_match(ranking, true_fact, threshold): 
        match = False
        for i in range(0,int(threshold)):
            try:
                if ranking[i][0] == true_fact:
                    match = True
            except:
                # It may happen that the threshold is bigger than the size of the rank, in which case we do nothing. 
                pass
        return match 


#  This method computes the hits-at-k metric in the way stated in Aurora's paper. 
def evaluate(examples_folder, predictions, rank_threshold, output) :
    
    #  Define paths of examples files 
    positive_examples_file = examples_folder + "/test-fact.txt"
    negative_head_examples_file = examples_folder + "/hits_negative_examples/heads.txt"
    negative_body_examples_file = examples_folder + "/hits_negative_examples/bodies.txt"
    negative_tail_examples_file = examples_folder + "/hits_negative_examples/tails.txt"
   
    #  Extract all examples from the input
    positive_examples = parse_facts(positive_examples_file) 
    negative_head_examples = parse_facts(negative_head_examples_file) 
    negative_body_examples = parse_facts(negative_body_examples_file) 
    negative_tail_examples = parse_facts(negative_tail_examples_file) 

    #  Construct a dictionary mapping each fact to its score
    scores_dict = {}
    for line in open(predictions, "r").readlines():
        ent1, ent2, ent3, ent4 = line.split()
        if ent4.endswith('\n'):
            ent4 = ent4[:-1]
        fact = (ent1, ent2, ent3)
        scores_dict[fact]=float(ent4)

    #  Throw warning if there are examples that have not been given scores.
    number_examples_without_score = 0 
    all_examples = positive_examples.union(negative_head_examples).union(negative_body_examples).union(negative_tail_examples)
    for example in all_examples:
        if example not in scores_dict:
            number_examples_without_score += 1
    if number_examples_without_score > 0:
        print("WARNING: no score was found for {} examples out of a total of {}".format(number_examples_without_score,len(all_examples)))


    #  Compute the number of Hits for the head
    number_of_matches = 0
    for true_fact in positive_examples:
        (head, body, tail) = true_fact
        # assert true_fact in scores_dict, "CRITICAL ERROR: No score detected for positive example {} {} {}. Shutting down.".format(head,body,tail)
        # Start the ranking as a list, we will order by score later. 
        ranking = [[true_fact,scores_dict.get(true_fact,0)]]
        # Look for up to 50 head corruptions of the true fact. 
        counter = 0
        for neg_example in negative_head_examples:
            (ne_head, ne_body, ne_tail) = neg_example
            if ne_body == body and ne_tail == tail and counter <= 50:
                counter += 1
                ranking += [[neg_example,scores_dict.get(neg_example,0)]]
        # Sort ranking at random, to avoid having several facts with same score where the right one just happens to go first.
        random.shuffle(ranking)
        # Order ranking by score, decreasing 
        ranking.sort(key = lambda i:i[1], reverse=True)         
        #  Check if there is a match for the first k elements, with k the rank threshold 
        if check_for_match(ranking, true_fact, rank_threshold):
            number_of_matches += 1
    hits_head = number_of_matches/len(positive_examples)

    #  Count the number of positive examples that do not use the `type` relation. These are the only ones we consider for body ranking.
    number_of_binary_positive_examples = 0
    for fact in positive_examples:
        (head, body, tail) = fact
        if body != "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>":
            number_of_binary_positive_examples += 1
    
    #  Compute the body ranking (excluding positive examples with `type` relation - note that relation corruptions never use `type` either).
    number_of_matches = 0
    for true_fact in positive_examples:
        (head, body, tail) = true_fact
        #  We do not measure the hits-r if the body is the type predicate
        if body != "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>":
            # Start the ranking as a list, we will order by score later. 
            ranking = [[true_fact,scores_dict.get(true_fact,0)]]
            # Look for up to 50 body corruptions of the true fact 
            counter = 0
            for neg_example in negative_body_examples:
                (ne_head, ne_body, ne_tail) = neg_example
                if ne_head == head and ne_tail == tail and counter <= 50:
                    counter += 1
                    ranking += [[neg_example,scores_dict.get(neg_example,0)]]
            # Sort ranking at random, to avoid having several facts with same score where the right one just happens to go first.
            random.shuffle(ranking)
            # Order ranking by score, decreasing 
            ranking.sort(key = lambda i:i[1], reverse=True)         
            #  Check if there is a match for the first k elements, with k the rank threshold 
            if check_for_match(ranking, true_fact, rank_threshold):
                number_of_matches += 1
    hits_body = number_of_matches/number_of_binary_positive_examples

    #  Compute the Tail ranking
    number_of_matches = 0
    for true_fact in positive_examples:
        (head, body, tail) = true_fact
        # Start the ranking as a list, we will order it by score later.
        ranking = [[true_fact,scores_dict[true_fact]]] 
        # Look for up to 50 tail corruptions of the true fact 
        counter = 0
        for neg_example in negative_tail_examples:
            (ne_head, ne_body, ne_tail) = neg_example
            if ne_head == head and ne_body == body and counter <= 50:
                counter += 1
                ranking += [[neg_example,scores_dict.get(neg_example,0)]]
        # Sort ranking at random, to avoid having several facts with same score where the right one just happens to go first.
        random.shuffle(ranking)
        # Order ranking by score, decreasing 
        ranking.sort(key = lambda i:i[1], reverse=True)         
        #  Check if there is a match for the first k elements, with k the rank threshold 
        if check_for_match(ranking, true_fact, rank_threshold):
            number_of_matches += 1
        hits_tail = number_of_matches/len(positive_examples)

    with open(output,'a') as f:
        f.write("E-hits at {}: {}\n".format(rank_threshold, (hits_head+hits_tail)/2))
        print("E-hits at {}: {}".format(rank_threshold, (hits_head+hits_tail)/2))
        f.write("R-hits at {}: {}\n".format(rank_threshold, hits_body))
        print("R-hits at {}: {}".format(rank_threshold, hits_body))
        f.close()

if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('--truths', help = "Name of the folder with the examples. It should contain the positive examples in a file 'test-fact.txt', and a sub-folder 'hits_negative_examples' with files 'heads.txt', 'bodies.txt', and 'tails.txt' for the negative examples.") 
    parser.add_argument('--rank-threshold', help='Maximum threshold in the ranking where we search for the positive example. For example, write 3 to compute Hits@3')
    parser.add_argument('--predictions', help='File with all derived facts and their scores')
    parser.add_argument('--output', help='File where the obtained hit metrics will be recorded')
    args = parser.parse_args()

    evaluate(args.truths, args.predictions, args.rank_threshold, args.output)

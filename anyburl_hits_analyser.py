from argparse import ArgumentParser
from os.path import splitext
import os
import random

"""
This function calculates the hits-at-k metric for the output of a link prediction task produced
by AnyBURL.
    Arguments:
    'input' - file outputted by AnyBURL
    'rank_threshold' - natural number k, for this program to compute the hits-at-k metric
    'output_file' - the file where the results of the metric will be written
"""

#  This is an auxiliary method that extracts the facts (without duplicates) from a file of triples 
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

def analyse(scores, rank_threshold, examples_folder, output_file):

    positive_examples_file = examples_folder + "/test-fact.txt"
    negative_head_examples_file = examples_folder + "/hits_negative_examples/heads.txt"
    negative_body_examples_file = examples_folder + "/hits_negative_examples/bodies.txt"
    negative_tail_examples_file = examples_folder + "/hits_negative_examples/tails.txt"
    
    #  Extract all examples from the input
    positive_examples = parse_facts(positive_examples_file) 
    negative_head_examples = parse_facts(negative_head_examples_file) 
    negative_body_examples = parse_facts(negative_body_examples_file) 
    negative_tail_examples = parse_facts(negative_tail_examples_file) 
   
    # Read the input file 
    scoresFile = open(scores, "r")
    Lines = scoresFile.readlines()
    # Ensure the output file is created, and open manager for it
    output_document = open(output_file, 'w')
   
    # The function reads input file top to bottom, line by line.
    # The file is structured in groups of three lines, of this form:
    #   head body tail
    #   Heads: head1 score1 head2 score2 head3 score3...
    #   Tails: tail1 score1 tail2 score2 taild3 score3...
    # Every time we read a line of the first kind, we store its head, body, and tail,
    # in the following variables, overwriting the previous triple.
    currentHead = ""
    currentRelation = ""
    currentTail = ""
    
    # Auxiliary flag, active only the first iteration. 
    first_line = True

    # Auxiliary counters
    number_of_head_matches = 0
    number_of_tail_matches = 0
    number_of_positive_examples = 0
    
    # Vectors of pairs, where the first is an entity, and the second its corresponding score. 
    head_scores = [] 
    tail_scores = []
    
    for line in Lines:
        if line.startswith('Heads: '):
        # Get a list of each proposed head followed by its own prediction 
            # Remove word "Head: "from line 
            predictions = line[7:].split()
            iterator = iter(predictions)
            # Note that because we call 'next(iterator)', this for loop advances 2-by-2 
            for x in iterator:
                head_scores += [[x, float(next(iterator))]]
        # Get a list of each proposed tail followed by its own prediction 
        elif line.startswith('Tails: '):
            # Remove word "Tail: "from line 
            predictions = line[7:].split()
            iterator = iter(predictions)
            # Note that because we call 'next(iterator)', this for loop advances 2-by-2 
            for x in iterator:
                tail_scores += [[x, float(next(iterator))]]
        else:
            #  We have finished reading a group of 3 lines, so we check for matches. 
            
            #  First we filter out any score that is higher than the target score and its corresponding head
            #  is not among those in the set of negative examples, because this is how MeGaNN evaluates too.
            if currentHead in head_scores:
                real_head_score = head_scores[currentHead]
                for h in head_scores:
                    if h != currentHead and (h, currentRelation, currentTail) not in negative_head_examples and head_scores[h] >= real_head_score:
                        del head_scores[h]
            if currentTail in tail_scores:
                real_tail_score = tail_scores[currentTail]
                for t in tail_scores:
                    if t != currentTail and (currentHead, currentRelation, t) not in negative_tail_examples and tail_scores[t] >= real_tail_score:
                        del tail_scores[t]

            #  Check if there was a head match 
            match = False 
            #  We shuffle the vector of candidates because AnyBURL often produces multiple candidates with the 
            #  exactly the same score (up to every decimal number), the first of which is often the true answer.
            #  Putting the correct answer always first unfairly benefits the metric, especially when the threshold is low.
            #  so we correct it by randomly shuffling the vector of candidates before ranking it by score.
            random.shuffle(head_scores)
            #  Rank vector by scores. 
            head_scores.sort(key = lambda i:i[1], reverse=True) 
            #  Check if the true head matches the prediction of the first k elements in the ranking, for k = rank_threshold. 
            for i in range(0,int(rank_threshold)):
                try:
                    if head_scores[i][0] == currentHead:
                        match = True
                #  Sometimes this throws an index_out_of_bounds exception because AnyBURL did not find any other fact, so the score is 0. 
                except:
                    if not first_line:
                        print("WARNING: Not enough head predictions for fact {} {} {}".format(currentHead, currentRelation, currentTail)) 
                    else: 
                        None
            if match:
                number_of_head_matches += 1
            #  Reset auxiliary variable
            head_scores = []
            #  Check if there was a tail match 
            match = False 
            random.shuffle(tail_scores)
            tail_scores.sort(key = lambda i:i[1], reverse=True) 
            for i in range(0,int(rank_threshold)):
                try:
                    if tail_scores[i][0] == currentTail:
                        match = True
                except:
                    if not first_line:
                        print("WARNING: Not enough tail predictions for fact {} {} {}".format(currentHead, currentRelation, currentTail))
                    else:
                        None
            if match:
                number_of_tail_matches += 1
            #  Reset auxiliary variables
            match = False
            tail_scores = []
            #  Update invariants
            currentHead, currentRelation, currentTail = line.split()
            #Remove the end of line character 
            if currentTail.endswith('\n'):
                currentTail = currentTail[:-1]
            number_of_positive_examples += 1
            if first_line:
                first_line = False

    hits_head = number_of_head_matches/number_of_positive_examples
    hits_tail = number_of_tail_matches/number_of_positive_examples
    print("E-hits at {}: {}".format(rank_threshold, (hits_head+hits_tail)/2))
    output_document.write("E-hits at {}: {}".format(rank_threshold, (hits_head+hits_tail)/2))

if __name__ == '__main__':

    # Read the arguments from the command line
    parser = ArgumentParser()
    parser.add_argument('--scores',help="File with the scores for each fact")
    parser.add_argument('--rank-threshold',help="Rank chosen for ordering")
    parser.add_argument('--examples-folder',help="Folder where all examples are; the structure must be as usual")
    parser.add_argument('--output',help="File where we store the result") 
    args = parser.parse_args()

    analyse(args.scores, args.rank_threshold, args.examples_folder, args.output)



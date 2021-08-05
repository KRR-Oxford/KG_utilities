'''
This piece of script takes as input a prediction file produced by anyburl, and a threshold number between 0 and 1, and then
extracts a list of all the facts that have been *predicted* with a score equal or above the threshold.
'''

from argparse import ArgumentParser
from os.path import splitext
from numpy import arange
from numpy import trapz
from numpy import nan_to_num
import random


def process(predictions_with_scores):
    # Read the corresponding file
    inputFile = open(predictions_with_scores, "r")
    Lines = inputFile.readlines()

    # This function reads the input file from top to bottom, line by line.
    # The files produced by AnyBURL should be structured in groups of three lines, of this form:
    #   head body tail
    #   Heads: head1 score1 head2 score2 head3 score3...
    #   Tails: tail1 score1 tail2 score2 taild3 score3...
    # Every time we read a line of the first kind, we store its head, body, and tail,
    # in the following variables, overwriting the previous triple.
    currentHead = ""
    currentTail = ""
    currentRelation = ""

    facts_to_sum_of_scores = {} 
    facts_to_occurrences = {}

    #  First we extract the facts and scores, aggregating scores of a fact 
    for line in Lines:
        if line.startswith('Heads: '):
            predictions = line[7:].split()
            iterator = iter(predictions)
            for x in iterator:
                fact = (x, currentRelation, currentTail)
                score = next(iterator)
                facts_to_sum_of_scores[fact] = facts_to_sum_of_scores.get(fact,0) + float(score)  
                facts_to_occurrences[fact] = facts_to_occurrences.get(fact,0) + 1 
        elif line.startswith('Tails: '):
            for x in iterator:
                fact = (currentHead, currentRelation, x)
                score = next(iterator)
                facts_to_sum_of_scores[fact] = facts_to_sum_of_scores.get(fact,0) + float(score)  
                facts_to_occurrences[fact] = facts_to_occurrences.get(fact,0) + 1 
        else:
            currentHead, currentRelation, currentTail = line.split()
            #Remove the end of line character 
            if currentTail.endswith('\n'):
                currentTail = currentTail[:-1]
    
    #  Next we average facts with the same score
    facts_to_average_of_scores = {} 
    for fact in facts_to_sum_of_scores:
        facts_to_average_of_scores[fact] = facts_to_sum_of_scores[fact]/facts_to_occurrences[fact]

    return facts_to_average_of_scores


def evaluate(facts_to_scores_dict, truths, output_file):
#        threshold_list = [0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2,0.1,0.05,0.02,0.01,0.005,0.002,0.001]):

    threshold_list = [0.0000000001,0.000000001,0.000000001,0.00000001,0.0000001,0.000001,0.00001,0.0001,0.001] + arange(0.01,1,0.01).tolist()
    threshold_list = [ round(elem,10) for elem in threshold_list]

    number_of_positives = 0
    number_of_negatives = 0
  
    num_scored_facts = 0 
    num_unscored_facts = 0
    num_unscored_negative_facts = 0
    
    # This stores the result. Each threshold is mapped to a 4-tuple containing true and false positives and negatives.
    threshold_to_counter = {} 
    entry_for = {"true_positives":0, "false_positives":1, "true_negatives":2, "false_negatives":3}
    threshold_to_counter[0] = [0,0,0,0]
    for threshold in threshold_list:
        threshold_to_counter[threshold] = [0,0,0,0]
  
    debug_flag = False
    LinesTruths = open(truths, 'r').readlines()
    for line in LinesTruths:
        head, relation, tail, truth = line.split()
        # Remove end-of-line character 
        if truth.endswith('\n'): 
            truth = truth[:-1]
        # Check that there is a score for this fact 
        try:
            facts_to_scores_dict[(head, relation, tail)]
            num_scored_facts += 1
        except:
            if not debug_flag: 
                 print("WARNING: No score detected for fact: \n {} \n {} \n {}".format(head, relation, tail))
                 debug_flag = True  
            num_unscored_facts += 1
        # Positive example 
        if truth == '1':
            number_of_positives +=1
            # First consider threshold 0
            # True positive 
            if facts_to_scores_dict.get((head, relation, tail),0) > 0:
                threshold_to_counter[0][entry_for["true_positives"]] +=  1      
            # False negative
            else:
                threshold_to_counter[0][entry_for["false_negatives"]] +=  1      
            # Consider all other thresholds 
            for threshold in threshold_list:
                # True positive 
                if facts_to_scores_dict.get((head, relation, tail),0) >= threshold:
                    threshold_to_counter[threshold][entry_for["true_positives"]] +=  1      
                # False negative
                else:
                    threshold_to_counter[threshold][entry_for["false_negatives"]] +=  1      
        # Negative example 
        else: 
            assert truth == '0', "ERROR: No truth value detected for line {}".format(line)
            try:
                facts_to_scores_dict[(head, relation, tail)]
            except:
                num_unscored_negative_facts += 1
            number_of_negatives +=1
            # First consider threshold 0 
            # False positive 
            if facts_to_scores_dict.get((head, relation, tail),0) > 0:
                threshold_to_counter[0][entry_for["false_positives"]] +=  1      
            # True negative
            else:
                threshold_to_counter[0][entry_for["true_negatives"]] +=  1      
            # Consider all other thresholds 
            for threshold in threshold_list:
                # False positive 
                if facts_to_scores_dict.get((head, relation, tail),0) >= threshold :
                    threshold_to_counter[threshold][entry_for["false_positives"]] +=  1      
                # True negative
                else:
                    threshold_to_counter[threshold][entry_for["true_negatives"]] +=  1      
  
    print("DATASET: {}".format(output_file))
    print("Number of unscored facts: {}, of which {} were negative".format(num_unscored_facts, num_unscored_negative_facts))
    print("Number of scored facts: {}".format(num_scored_facts))

    #  Compute and print result 
    recall_vector = []
    precision_vector = []
    with open(output_file, 'w') as f:
        f.write("Threshold" + '\t' + "Precision" + '\t' + "Recall"+ '\t' + "Accuraccy"+ '\t' + "F1 Score" + '\n')
        for threshold in threshold_to_counter:
            tp,fp,tn,fn = threshold_to_counter[threshold]
            f.write("{}\t{}\t{}\t{}\t{}\n".format(threshold, precision(tp,fp,tn,fn),
                recall(tp,fp,tn,fn), accuracy(tp,fp,tn,fn), f1score(tp,fp,tn,fn)))
            recall_vector.append(recall(tp,fp,tn,fn))
            precision_vector.append(precision(tp,fp,tn,fn))
        recall_vector = nan_to_num(recall_vector)
        precision_vector = nan_to_num(precision_vector)
        f.write("Area under precision recall curve: {}".format(auprc(precision_vector, recall_vector)))
        f.close()    


def precision(tp,fp,tn,fn):
    value = 0 
    try:
        value = tp/(tp+fp)
    except:
        value = float("NaN")
    finally:
        return value


def recall(tp,fp,tn,fn):
    value = 0 
    try:
        value = tp / (tp+fn) 
    except:
        value = float("NaN")
    finally:
        return value


def accuracy(tp,fp,tn,fn):
    value = 0 
    try:
        value = (tn+tp)/(tp+fp+tn+fn) 
    except:
        value = float("NaN")
    finally:
        return value


def f1score(tp,fp,tn,fn):
    value = 0 
    try:
        value = tp/(tp +  0.5*(fp+fn))
    except:
        value = float("NaN")
    finally:
        return value

#def specificity(tp,fp,tn,fn):
#    value = 0
#    try:
#        value = fp/(fp+tn)
#    except: 
#        value = float("NaN")
#    finally:
#        return value

def auprc(precision_vector, recall_vector):
    return -1 * trapz(precision_vector, recall_vector)

if __name__ == '__main__': 
    # Read the arguments from the command line
    parser = ArgumentParser()
    parser.add_argument('--scores',help="File containing scores for each positive and negative example.")
    parser.add_argument("--truths", help= "File containing the truth values for each positive and negative example.")
    parser.add_argument("--output", help="File where the result of the metrics calculation will be stored.")
    args = parser.parse_args()

    dict_facts_to_scores = process(args.scores)
    evaluate(dict_facts_to_scores, args.truths, args.output)





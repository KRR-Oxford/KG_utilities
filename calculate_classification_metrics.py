from argparse import ArgumentParser
from os.path import splitext
from numpy import arange
from numpy import trapz
from numpy import nan_to_num
import random

#  This constructs a dictionary from each fact to its score
def extract_scores(scores_file):
    scores_dict = {}
    for line in open(scores_file, "r").readlines():
        ent1, ent2, ent3, ent4 = line.split()
        if ent4.endswith('\n'):
            ent4 = ent4[:-1]
        fact = (ent1, ent2, ent3)
        scores_dict[fact]=float(ent4)
    return scores_dict


def evaluate(facts_to_scores_dict, truths, output_file):
#        threshold_list = [0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2,0.1,0.05,0.02,0.01,0.005,0.002,0.001]):

    threshold_list = arange(0,1,0.001).tolist()
    threshold_list = [ round(elem,4) for elem in threshold_list]

    number_of_positives = 0
    number_of_negatives = 0
   
    # This stores the result. Each threshold is mapped to a 4-tuple containing true and false positives and negatives.
    threshold_to_counter = {} 
    entry_for = {"true_positives":0, "false_positives":1, "true_negatives":2, "false_negatives":3}
    for threshold in threshold_list:
        threshold_to_counter[threshold] = [0,0,0,0]
   
    LinesTruths = open(truths, 'r').readlines()
    for line in LinesTruths:
        head, relation, tail, truth = line.split()
        # Remove end-of-line character 
        if truth.endswith('\n'): 
            truth = truth[:-1]
        # Positive example 
        if truth == '1':
            number_of_positives +=1
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
            number_of_negatives +=1
            for threshold in threshold_list:
                # False positive 
                if facts_to_scores_dict.get((head, relation, tail),0) >= threshold :
                    threshold_to_counter[threshold][entry_for["false_positives"]] +=  1      
                # True negative
                else:
                    threshold_to_counter[threshold][entry_for["true_negatives"]] +=  1      
    
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
    parser.add_argument('--scores',
            help='Name of the file with all derived facts and their scores')
    parser.add_argument('--truths',
            help='Name of the file with all positive and negative examples, with their truth values')
    parser.add_argument('--output',
            help='File where the obtained metrics will be recorded')
    args = parser.parse_args()

    dict_facts_to_scores = extract_scores(args.scores)
    evaluate(dict_facts_to_scores, args.truths, args.output)







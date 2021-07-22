from argparse import ArgumentParser
from random import randint
import os
import divide
import calculate_classification_metrics 

# Read the argument from command line 
parser = ArgumentParser()
parser.add_argument('--predictions', help="Name of the folder with the predicted facts and scores")
parser.add_argument('--truths', help="Name of the root folder with the truth values")
parser.add_argument('--truths-file', help="Within the dataset directory, path of the file with truths.")
parser.add_argument('--output', help="Name of the folder wherre we write the output")
args = parser.parse_args()

# Ensure that argments are valid folders
assert os.path.exists(args.predictions)
assert os.path.exists(args.truths)
assert os.path.exists(args.output)

# Read the corresponding files
for dataset_name in os.listdir(args.predictions):
    predictions_file = args.predictions + '/' + dataset_name 
    truths_file = args.truths + "/" + dataset_name + '/' + args.truths_file 
    output_file = args.output + '/' + dataset_name 
    print("Attempting to compute classification metrics for predictions file \n {} truths file \n {} output \n {}".format(predictions_file,truths_file,output_file)) 

    if os.path.exists(predictions_file) and os.path.exists(truths_file): 
        facts_to_scores = calculate_classification_metrics.extract_scores(predictions_file)
        calculate_classification_metrics.evaluate(facts_to_scores, truths_file, output_file)
        print("Success")

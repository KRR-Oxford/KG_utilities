from argparse import ArgumentParser
from random import randint
import os
import divide
import calculate_hits_metrics 

# Read the argument from command line 
parser = ArgumentParser()
parser.add_argument('--predictions', help="Root folder where all dataset folders with all predictions are.")
parser.add_argument('--truths', help="Root folder where all dataset folders with the truths are. We presume that inside each dataset folder, the structure is test/test-fact.txt for positive,\
        and test/hits_negative_examples/{heads/bodies/tails}.txt")
parser.add_argument('--output', help="Output folder to write the metrics to")
args = parser.parse_args()

# Ensure that input is a valid folder
assert os.path.exists(args.predictions)
assert os.path.exists(args.truths)
assert os.path.exists(args.output)

# Read the corresponding files
for dataset_name in os.listdir(args.predictions):
    predictions_file = args.predictions + '/' + dataset_name 
    truths_folder = args.truths + "/" + dataset_name + "/test"
    output_file = args.output + '/' + dataset_name 
    print("Attempting to compute classification metrics for \n PREDICTIONS: {} \n TRUTHS ROOT FOLDER: {} \n OUTPUT: {}".format(predictions_file,truths_folder, output_file)) 

    if os.path.exists(predictions_file) and os.path.exists(truths_folder): 
        #  This removes previous content from the metrics file. 
        with open(output_file, 'w') as f:
            f.write("E-hits and R-hits metrics\n")
            f.close() 
        #  Calculate and write the metrics.
        for k in range(1,11):
            calculate_hits_metrics.evaluate(truths_folder, predictions_file, k, output_file)
        print("Success")





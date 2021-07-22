from argparse import ArgumentParser
from random import randint
import os
import divide
import anyburl_hits_analyser

# Read the argument from command line 
parser = ArgumentParser()
parser.add_argument('--predictions',help="Parent folder with the dataset folders with the predictions")
parser.add_argument('--rank-threshold',help="Rank chosen for ordering")
parser.add_argument('--examples-folder',help="Folder where all examples are; the structure must be as usual")
parser.add_argument('--output',help="File where we store the result") 
args = parser.parse_args()

# Ensure that input is a valid folder
assert os.path.exists(args.predictions)
assert os.path.exists(args.examples_folder)
assert os.path.exists(args.output)

# Read the corresponding files
for dataset in os.listdir(args.predictions): 
    try:
        predictions_file = args.predictions + '/' + dataset + '/alpha-10' 
        examples_path = args.examples_folder + '/' + dataset + '/test'        
        output_file = args.output + '/' + dataset + '.txt'
        anyburl_hits_analyser.analyse(predictions_file, args.rank_threshold, examples_path, output_file)
    except:
        print("Error for dataset {}".format(dataset))

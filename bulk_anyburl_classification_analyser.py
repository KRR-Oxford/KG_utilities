from argparse import ArgumentParser
from random import randint
import os
import divide
import anyburl_classification_analyser

# Read the argument from command line 
parser = ArgumentParser()
parser.add_argument('--predictions', help="Root folder where all datasets folders with predictions are.")
parser.add_argument('--truths', help="Root folder where all datasets folders with truths are.")
parser.add_argument('--truths-file', help="Given a dataset folder, path of the file with the truths")
parser.add_argument('--output', help="Folder where outputs are written.")
args = parser.parse_args()

# Ensure that argments are valid folders
assert os.path.exists(args.predictions)
assert os.path.exists(args.truths)
assert os.path.exists(args.output)

# Read the corresponding files
for folder in [x[0] for x in os.walk(args.predictions)]:
    input_folder_name = os.path.basename(folder) 
   
    predictions_file = folder + '/alpha-10' 
    truths_file = args.truths + "/" + input_folder_name +  args.truths_file
    output_file = args.output + '/' + input_folder_name + '.txt'
    
    if os.path.exists(predictions_file) and os.path.exists(truths_file): 
        facts_to_scores = anyburl_classification_analyser.process(predictions_file)
        anyburl_classification_analyser.evaluate(facts_to_scores, truths_file, output_file)

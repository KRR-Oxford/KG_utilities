from argparse import ArgumentParser
import os
import predicate_extractor_MeGaNN

# Read the argument from command line
parser = ArgumentParser()
parser.add_argument("root_folder")
parser.add_argument("predicates_folder")
args = parser.parse_args()

# Ensure that input is a valid folder
assert os.path.exists(args.root_folder)
# Ensure that input is a valid folder
assert os.path.exists(args.predicates_folder)

# Read the corresponding files
for folder in [x[0] for x in os.walk(args.root_folder)]:
    target_file = folder + '/train/train.txt' 
    dataset_name = os.path.basename(folder)
    if os.path.exists(target_file): 
        output_file = predicate_extractor_MeGaNN.extract_predicates(target_file, dataset_name, args.predicates_folder)
        print("Extracted predicates in file {} to {}".format(target_file, output_file) )


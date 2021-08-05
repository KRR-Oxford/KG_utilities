from argparse import ArgumentParser
from random import randint
import os
import generate_negative_examples_classification_beta 

def get_targets(config_file):

    input_file= open(config_file,'r')
    lines = input_file.readlines()

    root = ""
    list_of_targets = []

    for target in lines:
        if target.endswith('\n'):
            target = target[:-1]
        if target.startswith("ROOT"):
            root = target.split('=')[1]
        elif os.path.isfile(root + '/' + target):
            list_of_targets.append(root + '/' + target)

    return list_of_targets 

# Read the argument from command line 
parser = ArgumentParser()
parser.add_argument('--config', help="Configuration file with the address of all datasets you wish to split.")
args = parser.parse_args()


for graph,facts in zip(get_targets(args.config)[0::2],get_targets(args.config)[1::2]):
    print("Creating negative examples for:" + '\n' + graph + '\n' + facts)
    generate_negative_examples_classification_beta.generate_negatives(graph,facts)
    print("Done.")


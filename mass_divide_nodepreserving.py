from argparse import ArgumentParser
from random import randint
import os
import divide_nodepreserving
from config_reader import get_targets

# Read the argument from command line 
parser = ArgumentParser()
parser.add_argument('--config', help="Configuration file with the address of all datasets you wish to split.")
parser.add_argument('--ratio', help="Maximum ratio of dataset to positive examples size." )
args = parser.parse_args()

for dataset in get_targets(args.config):
    print("Dividing facts in {}...".format(dataset))
    divide_nodepreserving.split_1_to_k(dataset,args.ratio)
    print("Done.")


from argparse import ArgumentParser
from os.path import splitext
import os

# Read the argument from command line
parser = ArgumentParser()
parser.add_argument("input")
args = parser.parse_args()

with open(args.input, "r") as f:
    for line in f:
        if line.endswith('0'+'\n'):
            newfile += line 
    f.close()
with open(path, "w") as f:
    for line in newfile:
        f.write(line)
f.close()



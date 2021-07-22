from argparse import ArgumentParser
from os.path import splitext
import os

# Read the argument from command line
parser = ArgumentParser()
parser.add_argument("folder")
args = parser.parse_args()

for subfolder in os.walk(args.folder):
    if subfolder[0].endswith("test-random-sample"):
        os.makedirs(subfolder[0] + "/negatives_only", exist_ok=True)
        for file in subfolder[2]:
            print("Identified file: \n" + subfolder[0]+ '/' + file)
            newfile = subfolder[0] + "/negatives_only/" + file
            if file.startswith("test") and file.endswith(".txt"): 
                with open(newfile, "w") as n:
                    with open(subfolder[0] + '/' + file, "r") as f:
                        for line in f:
                            if line.endswith('0'+'\n'):
                                # Remove negative score and previous tab separation 
                                n.write(line[:-3]+ '\n')
                    f.close()
                n.close()
                print("Extracted negative examples from: \n {}\n into\n {}".format(file,newfile))


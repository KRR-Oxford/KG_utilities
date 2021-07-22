from argparse import ArgumentParser
from os.path import splitext
import os

# Read the argument from command line
parser = ArgumentParser()
parser.add_argument('--root-folder',help="Root folder where all datasets are.")
parser.add_argument('--target-file-name',help="In each dataset, name of the file with the scores.")
parser.add_argument('--target-folder-name',help="In each dataset, name of the folder where the scores are.")
args = parser.parse_args()

for subfolder in os.walk(args.root_folder):
    if subfolder[0].endswith(args.target_folder_name):
        os.makedirs(subfolder[0] + "/no_scores", exist_ok=True)
        for file in subfolder[2]:
            print("Identified file: \n" + subfolder[0]+ '/' + file)
            newfile = subfolder[0] + "/no_scores/" + file
            if file.endswith(args.target_file_name):
                with open(newfile, "w") as n:
                    with open(subfolder[0] + '/' + file, "r") as f:
                        for line in f:
                            # Remove negative score and previous tab separation 
                            n.write(line[:-3]+ '\n')
                    f.close()
                n.close()
                print("Removed scores from: \n {}\n into resulting file \n {}".format(file,newfile))


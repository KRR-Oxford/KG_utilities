from argparse import ArgumentParser
from os.path import splitext
import os

# Read the argument from command line
parser = ArgumentParser()
parser.add_argument("input")
args = parser.parse_args()

for root, dirs, files in os.walk(args.input):
    for name in files:
        if name.endswith(".txt"):
            path = root + '/' + name
            print("Adding constant to " + path) 
            newfile = [] 
            with open(path, "r") as f:
                for line in f:
                    try: 
                        ent = line.split(None,4)
                        ent1 = ent[0]
                        ent2 = ent[1] 
                        ent3 = ent[2]
                        ent4 = ""
                        try:
                            ent4 = ent[3]
                        except:
                            ent4 = ""
                        if ent3.endswith('\n'):
                            ent3 = ent3[:-1]
                        ent1 = 'c'+ent1
                        ent2 = 'c'+ent2
                        ent3 = 'c'+ent3
                        if len(ent) == 3:
                            newfile += "{}\t{}\t{}\n".format(ent1,ent2,ent3)
                        else:
                            newfile += "{}\t{}\t{}\t{}\n".format(ent1,ent2,ent3,ent4)
                    except:
                        print("Ignoring line: "+ line)
                f.close()
            with open(path, "w") as f:
                for line in newfile:
                    f.write(line)



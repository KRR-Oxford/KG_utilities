import os

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

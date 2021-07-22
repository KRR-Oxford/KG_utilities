from argparse import ArgumentParser
import requests

parser = ArgumentParser()
parser.add_argument('--input', help="File with all the rules")
args = parser.parse_args()

rdfox_server = "http://localhost:8080"
type_predicate = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type' 

def parse_rule(rule):
    # Parse rule in current line 
    assert line.count(':-') == 1, "More than one head/body separator ':-' found. This script can't handle that (but it can handle the truth)." 
    head, body = line.split(' :- ')
    body = body.split(', ')
    if body[-1].endswith(' .\n'):
        body[-1] = body[-1][:-3]
    return head, body
    
def factify(atom):
    # Assume atoms end with [?a,?b] or [?a], for variables 'a' and 'b' 
    assert atom[-1] == ']' and (atom[-7] == '[' or atom[-4] == '['), "Did not recognise the predicate of atom {}".format(atom) 
    if atom[-7] == '[' :
        # Binary predicate 
        predicate = atom[:-7]
        # Use variable names as constants 
        constant1 = atom[-5]
        constant2 = atom[-2]
        return '<{}> {} <{}> .\n'.format(constant1, predicate, constant2)
    else:
        # Unary predicate
        predicate = atom[:-4]
        constant1 = atom[-2]
        return '<{}> <{}> {} .\n'.format(constant1, type_predicate, predicate)  

def assert_response_ok(response, message):
    '''Helper function to raise an exception if the REST endpoint returns an
    unexpected status code.'''
    if not response.ok:
        raise Exception(
            message + "\nStatus received={}\n{}".format(response.status_code,
                                                        response.text))

# Create data store in RDFox

rules = []
input_file = open(args.input, "r")
Lines = input_file.readlines()

print("{} rules read.".format(len(Lines)))
counter =0

for line in Lines:
   
    counter +=1
    if counter %10 == 0:
        print("Processed {} rules".format(counter))

    # Create data store in the RDF server, or reset it if it already exists.
    # print("Transforming body atoms into facts...") 
    if requests.get(rdfox_server + "/datastores").text == '?Name\n':
        # Create the datastore
        response = requests.post(rdfox_server + "/datastores/temp", params={'type': 'par-complex-nn'})
        assert_response_ok(response, "Failed to create datastore.")
    else:
        response = requests.delete(rdfox_server + "/datastores/temp/content")
        assert_response_ok(response, "Failed to clear content from datastore.")

    # print("Extracting head and body...") 
    head, body = parse_rule(line)
    # First redundancy check 
    if head in body: 
        continue

    # print("Loading dataset to RDFox...")
    # Extract dummy dataset and send to RDFox data store.
    for atom in body:
        response = requests.post( rdfox_server + "/datastores/temp/content", factify(atom))
        assert_response_ok(response, "Failed to add facts to datastore.")

    # print("Loading rules to RDFox...")
    # Extract all other rules and send them to RDFox data store.
    to_server = "" 
    for line2 in Lines: 
        if line2 != line:
            to_server += line2 
    response = requests.post( rdfox_server + "/datastores/temp/content", data=to_server)
    assert_response_ok(response, "Failed to add rule.")

    # print("Answering query...")
    # Return all entailed facts
    head_bits = factify(head).split()
    sparql_text = "SELECT ?p WHERE {{ ?p {} {}  }}".format(head_bits[1],head_bits[2])
    response = requests.get(rdfox_server + "/datastores/temp/sparql", params={"query": sparql_text})
    assert_response_ok(response, "Failed to run return entailed facts.") 
    candidates = response.text.split('\n')[1:-1]
    entailed = '<http://oxfordsemantic.tech/RDFox/' + head_bits[0][1:-1] + '>' in candidates
    if not entailed:
        rules += line

#  Write irreducible rules
minimal_rules_file = args.input + '_reduced.txt' 
with open(minimal_rules_file, 'w') as m:
    for rule in rules:
        m.write(rule)
    m.close()

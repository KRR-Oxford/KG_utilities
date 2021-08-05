from argparse import ArgumentParser


def create_truths(positive_examples_file,negative_examples_file,output_file):

    with open(output_file,'w') as output:
        for line in open(positive_examples_file,'r').readlines():
            if line.endswith('\n'):
                line = line[:-1]
            output.write(line + '\t' + '1' + '\n') 
        for line in open(negative_examples_file,'r').readlines():
            if line.endswith('\n'):
                line = line[:-1]
            output.write(line + '\t' + '0' + '\n') 

if __name__ == '__main__':
    
    parser = ArgumentParser()
    parser.add_argument('--positive_examples',help="File with positive examples")
    parser.add_argument('--negative_examples',help="File with negative examples")
    parser.add_argument('--output',help="Output file.")
    parser.add_argument('--config',help="File with a stream of arguments, so that this function can be called in bulk. Write the argument name followed by the list of arguments, one per line.")

    args = parser.parse_args()

    if args.config is not None:
        positive_examples_file_list = []
        negative_examples_file_list = []
        output_file_list = []
        current_list = None 
        for line in open(args.config,'r').readlines():
            if line.startswith("--positive_examples"):
                current_list = positive_examples_file_list
            elif line.startswith("--negative_examples"):
                current_list = negative_examples_file_list
            elif line.startswith("--output"):
                current_list = output_file_list
            else:
                if line.endswith('\n'):
                    line = line[:-1]
                current_list.append(line)
        assert len(positive_examples_file_list) == len(negative_examples_file_list) == len(output_file_list) 
        all_inputs = zip(positive_examples_file_list,negative_examples_file_list,output_file_list)
        for pos,neg,out in all_inputs:
            print("Joining files" + '\n' + pos + '\n' + neg)
            create_truths(pos,neg,out)
            print("Done")
    elif args.positve_examples is not None and args.negative_examples is not None and args.output is not None:
        print("Joining files" + '\n' + pos + '\n' + neg + '\n')
        create_truths(args.positive_examples,args.negative_examples,args.output)
        print("Done")
    else:
        print("No arguments were recognised. Shutting down...")
    



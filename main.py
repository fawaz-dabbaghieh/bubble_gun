import os
import sys
from core.functions import current_time
# import copy
from core.Graph import Graph
import argparse
import pdb


parser = argparse.ArgumentParser(description='Find Bubble Chains.')

parser.add_argument("-e", "--examples", dest="examples", action="store_true",
    help="prints out example commands to use the tool")

parser.add_argument("-g", "--in_graph", metavar="GRAPH_PATH", dest="in_graph", 
    default=None, type=str, help="graph file path (GFA or VG)")

parser.add_argument("-b", "--bubbles", metavar="OUTPUT_BUBBLES", dest="out_bubbles", 
    default=None, type=str, help="BubbleChains graph output path")
# parser.add_argument("-v", "--in_vg", dest="in_vg", metavar="GRAPH_PATH",
#     default=None, type=str, help="VG graph file path")
parser.add_argument("--only_simple", action="store_true",
	help="If used then only simple bubbles are detected")

parser.add_argument("-k", "--k_mer", dest="k_mer", metavar="k",
    default=0, type=int, help="K value of as integer")

parser.add_argument("-o", "--output", dest="graph_out", metavar="OUTPUT",
    type=str, default=None, help="Graph output file")

parser.add_argument("-s", "--start", dest="starting_nodes",
    metavar="START_NODES", type=int, nargs="+",
    default=None, help="Give the starting node(s) for neighborhood extraction")

parser.add_argument("-f", "--bfs", dest="bfs_len", metavar="SIZE", default=100,
    type=int, help="With -s --start option, size of neighborhood to extract")


args = parser.parse_args()

if len(sys.argv) == 1:
    print("You didn't give any arguments\n"
        "Try to use -h or --help for help\n"
        "Or -e --examples for examples to use the tool")
    sys.exit()

if args.examples:
    print("Here are some examples:")
    sys.exit()

if args.in_graph == None:
    print("you didn't give an input graph file")
    parser.print_help()
    sys.exit(0)

if args.k_mer == 0:
    print("WARNING! You did not give a k value."
        "The output statistics might not be accurate\n"
        "If the graph is bluntified ignore this warning.")

if args.out_bubbles != None:
    output_file = args.out_bubbles
    print("[{}] Reading Graph...".format(current_time()))
    graph = Graph(args.in_graph)
    graph.k = int(args.k_mer)
    print("[{}] Compacting graph...".format(current_time()))
    graph.compact()
    print("[{}] Finding chains...".format(current_time()))
    if args.only_simple:
    	graph.find_chains(only_simple=True)
    else:
    	graph.find_chains()
    pdb.set_trace()
    # print("{} Writing bubble to file".format(current_time()))
    # graph.write_b_chains(output=args.out_bubbles)


if args.starting_nodes != None:
    if args.bfs_len != None:
        if args.graph_out == None:
            print("Please specify an output file with -o --output")
            sys.exit()
        print("extracting neighborhood")

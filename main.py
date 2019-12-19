import os
import sys
import time
# import copy
from core.Graph2 import Graph
import argparse
import pdb

parser = argparse.ArgumentParser(description='Find Bubble Chains.')


# parser.add_argument('-f', '--foo', help='old foo help')
parser.add_argument("-e", "--examples", dest="examples", action="store_true",
	help="prints out example commands to use the tool")

parser.add_argument("-g", "--in_gfa", metavar="GRAPH_PATH", dest="in_gfa", 
	default=None, type=str, help="GFA graph file path")

parser.add_argument("-v", "--in_vg", dest="in_vg", metavar="GRAPH_PATH",
	default=None, type=str, help="VG graph file path")

parser.add_argument("-k", "--k_mer", dest="k_mer", metavar="k",
	default=0, type=int, help="K value of as integer")

parser.add_argument("-o", "--output", dest="graph_out", metavar="OUTPUT",
    type=str, default=None, help="Graph output file")

parser.add_argument("-s", "--start", dest="starting_nodes",
	metavar="START_NODES", type=int, nargs="+",
	default=None, help="Give the starting node(s) for neighborhood extraction")

parser.add_argument("-f", "--bfs", dest="bfs_len", metavar="SIZE", default=100,
	type=int, help="With -s --start option, size of neighborhood to extract")
# parser.add_argument('--sum', dest='accumulate', action='store_const',
# 					const=sum, default=max,
# 					help='sum the integers (default: find the max)')
# parser.add_argument('integers', metavar='N', type=int, nargs='+',
#					 help='an integer for the accumulator')




# parser.add_option("-g", "--in_gfa", action="store", dest="in_graph", default=None, type=str,
# 				  help="Give the gfa file destination here")

# parser.add_option("-k", "--k_mer", action="store", dest="k_mer", default=None, type=int,
# 				  help="Give the K as integer here")

# parser.add_option("--compact", action="store", dest="compact", type=str, default=None,
# 				  help="This option will compact your graph and output the compacted one, "
# 					   "give the output destination after this option")

# parser.add_option("--bfs", action="store_true", dest="bfs_start", default=False,
# 				  help="This option will do BFS from the start node given with a neighborhood of size n"
# 					   ", give the following arguments <input_gfa> <start_node_id> <n> <output_file>")

# parser.add_option("--find_bubbles", action="store_true", dest="find_bubbles", default=False,
# 				  help="This option will find bubble chains and print the statistics to terminal, "
# 					   "give the following arguments <input_gfa> <k>")

# parser.add_option("--out_bubbles", action="store", dest="output_bubbles", default=None, type=str,
# 				  help="Only be used after --bubbles, will output only bubble chains in a separate GFA file "
# 					   "the output file name is given after it. e.g.: --out_bubbles <output_gfa>")

# parser.add_option("--plot", action="store", dest="plot", default=None, type=str,
# 				  help="Only used after --bubbles, outputs statistics plots in the given directory, "
# 					   "e.g.: --plot <output_dir>")

# parser.add_option("--components_plot", action="store_true", dest="comp_plot", default=False,
# 				  help="Only used after --bubbles --plot, gives a histogram of the distribution of connected"
# 					   " components in the graph. e.g.: --components_plot <output_file>")

# parser.add_option("--plot_contigs_nobub", action="store_true", dest="plot_contigs_dist", default=False,
# 				  help="Only used after --bubbles and --components_plot, this will output the contigs "
# 					   "distribution of the graph after removing the bubble chains."
# 					   " e.g.: --plot_contigs_nobub <output_file_path.png>")

# parser.add_option("--output_component", action="store", dest="output_components", default=None, type=str,
# 				  help="If used after --bubbles, then you only need to give it one argument <output_gfa>"
# 					   " .If it was used alone then you need to give <input_gfa> <k> as raw argument to main. "
# 					   "Example: python main.py <input_gfa> <k> --output_component <output_gfa>")

args = parser.parse_args()

pdb.set_trace()
if args.examples:
	print("Here are some examples:")
	sys.exit()

if (args.in_gfa == None) and (args.in_vg == None):
	print("you didn't give an input graph file")
	parser.print_help()
	sys.exit(0)

if args.k_mer == 0:
	print("WARNING! You did not give a k value."
		"The output statistics might not be accurate")

if args.starting_nodes != None:
	if args.bfs_len != None:
		if args.graph_out == None:
			print("Please specify an output file with -o --output")
			sys.exit()
		print("extracting neighborhood")
	
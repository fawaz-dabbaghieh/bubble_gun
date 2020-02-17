import os
import sys
from core.functions import current_time, bfs
from core.Graph import Graph
from core.digest_gam import build_reads_dict
import argparse
import pdb
import logging
import pickle

parser = argparse.ArgumentParser(description='Find Bubble Chains.')

parser.add_argument("-e", "--examples", dest="examples", action="store_true",
    help="prints out example commands to use the tool")

parser.add_argument("-g", "--in_graph", metavar="GRAPH_PATH", dest="in_graph", 
    default=None, type=str, help="graph file path (GFA or VG)")

parser.add_argument("-b", "--bubbles", action="store_true",
    help="Finds bubble chains and prints statistics.")
# parser.add_argument("-v", "--in_vg", dest="in_vg", metavar="GRAPH_PATH",
#     default=None, type=str, help="VG graph file path")
parser.add_argument("--only_simple", action="store_true",
    help="If used then only simple bubbles are detected")

parser.add_argument("-k", "--k_mer", dest="k_mer", metavar="K",
    default=0, type=int, help="K value of as integer")

parser.add_argument("-c", "--compact", dest="compacted", metavar="COMPACTED",
    default=None, type=str, help="Output compacted file to path given")

parser.add_argument("-p", "--biggest_comp", dest="biggest_comp", metavar="BIG_COMP",
    default=None, type=str, help="Output biggest component to path given")

parser.add_argument("-s", "--start", dest="starting_nodes",
    metavar="START_NODES", type=int, nargs="+",
    default=None, help="Give the starting node(s) for neighborhood extraction")

parser.add_argument("-f", "--bfs", dest="bfs_len", metavar="SIZE", default=None,
    type=int, help="With -s --start option, size of neighborhood to extract")

parser.add_argument("-o", "--output", dest="graph_out", metavar="OUTPUT",
    type=str, default=None, help="Output neighborhood ")

parser.add_argument("-a", "--alignment", dest="gam_file", metavar="GAM",
    type=str, default=None, help="Take BAM file and output pickled dict")

args = parser.parse_args()

if len(sys.argv) == 1:
    print("You didn't give any arguments\n"
          "Try to use -h or --help for help\n"
          "Or -e --examples for examples to use the tool")
    sys.exit()

if args.gam_file is not None:
    print("[{}] reading gam file and building dict".format(current_time()))
    all_reads = build_reads_dict(args.gam_file)
    print("[{}] finished building dict, pickling it".format(current_time()))
    out_file = open("pickled_dict", "ab")
    pickle.dump(all_reads, out_file)
    out_file.close()
    print("[{}] finished successfully".format(current_time()))
    sys.exit()

if args.examples:
    print("Some example for using this tool\n\n"
          "You have a GFA graph and want to check some bubble statistics:\n"
          "bubblegun -g some_graph_file.gfa -k 61 > stats.log\n\n"
          "You want to output the bubble chains of only simple bubbles in a separate file:\n"
          "bubblegun -g graph_file.gfa -k 31 --bubbles --only_simple -o b_chains.gfa > stats.log\n\n"
          "You want to output bubble chains with both bubbles and Superbubbles:\n"
          "bubblegun -g graph_file.gfa -k 41 --bubbles -o b_sb_chains.gfa > stats.log")
    sys.exit()

if args.in_graph == None:
    print("you didn't give an input graph file")
    parser.print_help()
    sys.exit(0)

if args.k_mer == 0:
    print("WARNING! You did not give a k value."
          "The output statistics might not be accurate\n"
          "If the graph is bluntified ignore this warning.")

if (args.compacted != None) or (args.biggest_comp != None) or (args.bubbles):
    # output_file = args.out_bubbles
    print("[{}] Reading Graph...".format(current_time()))
    if args.k_mer == 0:
        graph = Graph(args.in_graph, 1)
    else:
        graph = Graph(args.in_graph, args.k_mer)

    if args.compacted != None:
        print("[{}] Compacting Graph...".format(current_time()))
        # pdb.set_trace()
        graph.compact()
        print("[{}] Writing Compacted Graph...".format(current_time()))
        graph.write_graph(output_file=args.compacted)

    if args.biggest_comp != None:
        graph.compact()
        print("[{}] Finding Biggest Component...".format(current_time()))
        biggest_comp = graph.biggest_comp()
        graph.reset_visited()
        print("[{}] Writing Biggset Component...".format(current_time()))
        graph.write_graph(output_file=args.biggest_comp,
            set_of_nodes=biggest_comp)

    if args.bubbles:
        # print("[{}] Compacting graph...".format(current_time()))
        # graph.compact()
        print("[{}] Finding chains...".format(current_time()))
        if args.only_simple:
            graph.find_chains(only_simple=True)
        else:
            graph.find_chains()

        graph.fill_bubble_info()
        print("Sequence coverage of the bubble chains is {}%".format(graph.chain_cov_seq()))
        print("Node coverage of the bubble chains is {}%".format(graph.chain_cov_node()))
        b_numbers = graph.bubble_number()
        print("The number of Simple Bubbles is {}\n"
              "The number of Superbubbles is {}\n"
              "The number of insertions is {}".format(b_numbers[0], b_numbers[1],
                  b_numbers[2]))
        print("The longest chain seq-wise has {} bp".format(graph.longest_chain_seq().length_seq(graph.k)))
        print("The longest chain bubble_wise has {} bubbles".format(len(graph.longest_chain_bubble())))


        if args.graph_out != None:
            graph.write_b_chains(output=args.graph_out)

if args.starting_nodes != None:
    if args.bfs_len != None:
        if args.graph_out == None:
            print("You need to give an output file name -o")
            sys.exit()
        
        print("[{}] Reading Graph...".format(current_time()))
        if args.k_mer == 0:
            graph = Graph(args.in_graph, 1)
        else:
            graph = Graph(args.in_graph, args.k_mer)

        for n in args.starting_nodes:
            print("extracting neighborhood")
            set_of_nodes = bfs(graph, n, args.bfs_len)
            graph.write_graph(set_of_nodes=set_of_nodes, 
                output_file=args.graph_out, append=True, modified=False)
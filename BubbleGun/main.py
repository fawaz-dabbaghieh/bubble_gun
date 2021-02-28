#!/usr/bin/env python3
import sys
import argparse
import logging
from BubbleGun.bfs import bfs
from BubbleGun.Graph import Graph
from BubbleGun.bubbles_fasta import write_bubbles
from BubbleGun.digest_gam import digest_gam
from BubbleGun.find_bubbles import find_bubble_chains
from BubbleGun.fasta_chains import output_chains_fasta
from BubbleGun.json_out import json_out
from BubbleGun.find_child_chains import find_children
from BubbleGun.output_certain_chains import write_certain_chains

parser = argparse.ArgumentParser(description='Find Bubble Chains.', add_help=True)
subparsers = parser.add_subparsers(help='Available subcommands', dest="subcommands")

parser._positionals.title = 'Subcommands'
parser._optionals.title = 'Global Arguments'

########################## general commands ###############################
parser.add_argument("-e", "--examples", dest="examples", action="store_true",
                    help="prints out example commands to use the tool")

parser.add_argument("-g", "--in_graph", metavar="GRAPH_PATH", dest="in_graph",
                    default=None, type=str, help="graph file path (GFA or VG)")

parser.add_argument("-k", "--k_mer", dest="k_mer", metavar="K",
                    default=0, type=int, help="K value of as integer (default is 1)")


parser.add_argument("--log", dest="log_level", type=str, default="DEBUG",
                    help="The logging level [DEBUG, INFO, WARNING, ERROR, CRITICAL]")

########################## Bubble chains options ###############################
bubble_parser = subparsers.add_parser('bchains', help='Command for detecting bubble chains')

bubble_parser.add_argument("--bubble_json", dest="out_json", default=None, type=str,
                           help="Outputs Bubbles, Superbubbles, and Chains as a JSON file")

bubble_parser.add_argument("--only_simple", action="store_true",
                           help="If used then only simple bubbles are detected")

bubble_parser.add_argument("--only_super", action="store_true",
                           help="If used then only simple bubbles are detected")

bubble_parser.add_argument("--save_memory", action="store_true", dest="low_memory",
                           help="Identifies bubble chain with less memory. No statistics outputted")

bubble_parser.add_argument("--chains_gfa", dest="chains_gfa", default=None, type=str,
                           help="Output only bubble chains as a GFA file")

bubble_parser.add_argument("--fasta", dest="out_fasta", metavar="FASTA",
                           type=str, default=None,
                           help="Outputs the bubble branches as fasta file (doesn't work with memory saving)")

bubble_parser.add_argument("--out_haplos", dest="out_haplos", action="store_true",
                           help="output randomly two haplotypes for each chain (doesn't work with memory saving)")

########################## Compact graph ###############################
compact_parser = subparsers.add_parser('compact', help='Command for compacting graphs')

compact_parser.add_argument(dest="compacted", metavar="PATH_COMPACTED",
                            default=None, type=str, help="Compacted graph output path")

########################## Biggest component ###############################
biggest_comp_parser = subparsers.add_parser('biggestcomp', help='Command for separating biggest component')

biggest_comp_parser.add_argument(dest="biggest_comp", metavar="PATH_BIG_COMP",
                                 default=None, type=str, help="Biggest component output path")

########################## BFS commands ###############################
bfs_parser = subparsers.add_parser('bfs', help='Command for separating neighborhood')

bfs_parser.add_argument("--start", dest="starting_nodes", metavar="START_NODES", type=str, nargs="+",
                        default=None, help="Give the starting node(s) for neighborhood extraction")

bfs_parser.add_argument("--neighborhood_size", dest="bfs_len", metavar="SIZE", default=None,
                        type=int, help="With -s --start option, size of neighborhood to extract")

bfs_parser.add_argument("--output_neighborhood", dest="output_neighborhood", metavar="OUTPUT",
                        type=str, default=None, help="Output neighborhood file")

########################## Digest gam ###############################
gam_parser = subparsers.add_parser('gamdigest', help='Command for digesting a gam file')

gam_parser.add_argument("--json_file", dest="json_file", metavar="JSON_FILE",
                        type=str, default=None, help="The JSON file wtih bubble chains information")

gam_parser.add_argument("--alignment_file", dest="gam_file", metavar="GAM",
                        type=str, default=None, help="Take GAM file and output pickled dict")

gam_parser.add_argument("--min_cutoff", dest="min_cutoff", type=int, default=None,
                        help="The minimum cutoff of a mapping length.")

gam_parser.add_argument("--out_dict", dest="pickle_out",
                        type=str, default=None,
                        help="A pickled dictionary output path. contains read_id:[nodes]")

########################## output chain ###############################
output_chain = subparsers.add_parser('chainout', help='Outputs certain chain(s) given by their id as a GFA file')
output_chain.add_argument("--json_file", dest="json_file", metavar="JSON_FILE",
                          type=str, default=None, help="The JSON file wtih bubble chains information")

output_chain.add_argument("--chain_ids", dest="chain_ids", metavar="CHAIN_IDS", type=str, nargs="+",
                          default=None, help="Give the chain Id(s) to be outputted")

output_chain.add_argument("--output_chain", dest="output_chain", metavar="OUTPUT",
                          type=str, default=None, help="Output path for the chains chosen")

args = parser.parse_args()

# log_file = "log_" + str(time.clock_gettime(1)).split(".")[0] + ".log"
log_file = "log.log"

logging.basicConfig(filename=log_file, filemode='w',
                    format='[%(asctime)s] %(message)s',
                    level=getattr(logging, args.log_level.upper()))

logging.info(" ".join(["argument given:"] + sys.argv))


def main():
    if len(sys.argv) == 1:
        print("You did not provide any arguments\n"
              "Try to use -h or --help for help\n"
              "Or -e --examples for examples to use the tool")
        sys.exit()

    if args.examples:
        # todo
        print("Some example for using this tool\n\n"
              "You have a GFA graph and want to check some bubble statistics:\n"
              "bubblegun -g some_graph_file.gfa -k 61 > stats.log\n\n"
              "You want to output the bubble chains of only simple bubbles in a separate file:\n"
              "bubblegun -g graph_file.gfa -k 31 --bubbles --only_simple -o b_chains.gfa > stats.log\n\n"
              "You want to output bubble chains with both bubbles and Superbubbles:\n"
              "bubblegun -g graph_file.gfa -k 41 --bubbles -o b_sb_chains.gfa > stats.log")
        sys.exit()

    if args.subcommands is None:
        print("Please provide a subcommand after the global commands")
        sys.exit(1)

    if args.in_graph is None:
        if args.subcommands != "gamdigest":
            print("you didn't give an input graph file")
            parser.print_help()
            sys.exit(0)

    if args.k_mer == 0:
        args.k_mer = 1

    ####################### chainout
    if args.subcommands == "chainout":
        if args.json_file is not None:
            if args.chain_ids is not None:
                if args.output_chain is not None:

                    logging.info("Reading Graph...")
                    if args.k_mer == 0:
                        graph = Graph(args.in_graph)
                    else:
                        graph = Graph(args.in_graph)

                    logging.info("Outputting chains chosen...")
                    write_certain_chains(args.json_file, graph, args.chain_ids, args.output_chain)

                else:
                    print("You did not provide the output file path")
                    sys.exit(1)
            else:
                print("You did not provide a chain id(s) to be outputted")
                sys.exit(1)
        else:
            print("You did not provide the JSON file with the chain information")
            sys.exit(1)

    ####################### gamdigest
    if args.subcommands == "gamdigest":
        if args.gam_file is not None:
            if args.pickle_out is not None:
                if args.min_cutoff is not None:
                    logging.info("reading gam file and building dict")
                    all_reads = digest_gam(args.in_graph, args.gam_file, args.min_cutoff, args.pickle_out)
                    logging.info("finished successfully")
                    # sys.exit()
                else:
                    print("You did not provide the minimum cutoff. Maybe something like 3 times the k-mer length")
                    sys.exit(1)
            else:
                print("You did not provide a path for the pickled dictionary output")
                sys.exit(1)
        else:
            print("Please provide the path to the gam file")
            sys.exit(1)

    ####################### compact graph
    if args.subcommands == "compact":
        if args.compacted is not None:
            logging.info("Reading Graph...")

            if args.k_mer == 0:
                graph = Graph(args.in_graph)
            else:
                graph = Graph(args.in_graph)
            logging.info("Compacting Graph...")
            graph.compact()
            logging.info("Writing Compacted Graph...")
            graph.write_graph(output_file=args.compacted)
            logging.info("Done...")
        else:
            print("Please provide the path for the output compacted graph")
            sys.exit(1)

    ####################### biggest component
    if args.subcommands == "biggestcomp":
        if args.biggest_comp is not None:
            logging.info("Reading Graph...")

            if args.k_mer == 0:
                graph = Graph(args.in_graph)
            else:
                graph = Graph(args.in_graph)
            logging.info("Finding Biggest Component...")
            biggest_comp = graph.biggest_comp()
            logging.info("Writing Biggset Component...")
            graph.write_graph(output_file=args.biggest_comp, set_of_nodes=biggest_comp)
            logging.info("Done...")
        else:
            print("Please provide the path for the biggest component graph")
            sys.exit(1)

    ####################### Bubbles
    if args.subcommands == "bchains":
        # output_file = args.out_bubbles
        if args.low_memory and (args.out_fasta is not None) or args.low_memory and (args.chains_gfa is not None):
            print("You cannot combine memory saving with --fasta or --chains_gfa")
            sys.exit(0)

        logging.info("Reading Graph...")
        if args.k_mer == 0:
            graph = Graph(args.in_graph)
        else:
            graph = Graph(args.in_graph, low_memory=args.low_memory)

        # print("[{}] Compacting graph...".format(current_time()))
        # graph.compact()
        # tracemalloc.start()
        logging.info("Finding chains...")

        find_bubble_chains(graph, only_simple=args.only_simple)
        # graph.find_chains(only_simple=args.only_simple)
        # I don't think I need to fill info here
        # I can do that if I am outputting a json
        find_children(graph)
        # graph.fill_bubble_info()
        logging.info("Done finding chains...")
        b_numbers = graph.bubble_number()
        print("The number of Simple Bubbles is {}\n"
              "The number of Superbubbles is {}\n"
              "The number of insertions is {}".format(b_numbers[0], b_numbers[1],
                                                      b_numbers[2]))
        if not args.low_memory:
            print("Sequence coverage of the bubble chains is {}%".format(graph.chain_cov_seq()))
            print("Node coverage of the bubble chains is {}%".format(graph.chain_cov_node()))
            print("The longest chain seq-wise has {} bp".format(graph.longest_chain_seq().length_seq()))
            print("The longest chain bubble_wise has {} bubbles".format(len(graph.longest_chain_bubble())))

        # snapshot = tracemalloc.take_snapshot()
        # BubbleGun.memory_profile.display_top(snapshot, limit=10)
        if args.out_json is not None:
            logging.info("Outputting bubble chains gfa...")
            json_out(graph, args.out_json)

        if args.chains_gfa is not None:
            logging.info("Outputting bubble chains gfa...")
            graph.write_b_chains(output=args.chains_gfa)

        if args.out_fasta is not None:
            logging.info("Outputting each bubble branch...")
            write_bubbles(graph, args.out_fasta)

        if args.out_haplos:
            logging.info("Outputting two random haplotypes of each bubble chain...")
            output_chains_fasta(graph)

        # h = guppy.hpy()
        # print(h.heap())
    ####################### BFS
    if args.subcommands == "bfs":
        if args.starting_nodes is not None:
            if args.bfs_len is not None:
                if args.output_neighborhood is not None:

                    logging.info("Reading Graph...")
                    if args.k_mer == 0:
                        graph = Graph(args.in_graph)
                    else:
                        graph = Graph(args.in_graph)

                    for n in args.starting_nodes:
                        logging.info("extracting neighborhood around node {}".format(n))
                        set_of_nodes = bfs(graph, n, args.bfs_len)
                        graph.write_graph(set_of_nodes=set_of_nodes,
                                          output_file=args.output_neighborhood, append=True, modified=False)
                        logging.info("finished successfully...")
                else:
                    print("You need to give an output file name --output_neighborhood")
                    sys.exit()
            else:
                print("You did not give the neighborhood size")
                sys.exit(1)
        else:
            print("You did not give the starting node(s)")


if __name__ == "__main__":
    main()

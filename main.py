#!/usr/bin/env python3
import sys
from BubbleGun.functions import current_time, bfs
from BubbleGun.Graph import Graph
from BubbleGun.bubbles_fasta import write_fasta
from BubbleGun.digest_gam import digest_gam
from BubbleGun.fasta_chains import output_chains_fasta
import argparse
import logging

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
                    default=0, type=int, help="K value of as integer")

parser.add_argument("--with_coverage", dest="coverage", action="store_true",
                    help="If this option given, mean coverage is taken from the GFA file")

parser.add_argument("--log", dest="log_level", type=str, default="DEBUG",
                    help="The logging level [DEBUG, INFO, WARNING, ERROR, CRITICAL]")

########################## Bubble chains options ###############################
bubble_parser = subparsers.add_parser('bchains', help='Command for detecting bubble chains')

bubble_parser.add_argument("--bubble_json", dest="out_json", default=None, type=str,
                           help="Outputs Bubbles, Superbubbles, and Chains as a JSON file")

bubble_parser.add_argument("--only_simple", action="store_true",
                           help="If used then only simple bubbles are detected")

bubble_parser.add_argument("--save_memory", action="store_true",
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

compact_parser.add_argument("--compact", dest="compacted", metavar="COMPACTED",
                            default=None, type=str, help="Output compacted file to path given")

########################## Biggest component ###############################
biggest_comp_parser = subparsers.add_parser('biggestcomp', help='Command for separating biggest component')

biggest_comp_parser.add_argument("--biggest_comp", dest="biggest_comp", metavar="BIG_COMP",
                                 default=None, type=str, help="Output biggest component to path given")

########################## BFS commands ###############################
bfs_parser = subparsers.add_parser('bfs', help='Command for separating neighborhood')

bfs_parser.add_argument("--start", dest="starting_nodes", metavar="START_NODES", type=int, nargs="+",
                        default=None, help="Give the starting node(s) for neighborhood extraction")

bfs_parser.add_argument("--neighborhood_size", dest="bfs_len", metavar="SIZE", default=None,
                        type=int, help="With -s --start option, size of neighborhood to extract")

bfs_parser.add_argument("--output_neighborhood", dest="output_neighborhood", metavar="OUTPUT",
                        type=str, default=None, help="Output neighborhood file")

########################## Digest gam ###############################
gam_parser = subparsers.add_parser('gamdigest', help='Command for digesting a gam file')
gam_parser.add_argument("--alignment_file", dest="gam_file", metavar="GAM",
                        type=str, default=None, help="Take GAM file and output pickled dict")

gam_parser.add_argument("--out_dict", dest="pickle_out",
                        type=str, default=None,
                        help="A pickled dictionary output path. contains read_id:[nodes]")

args = parser.parse_args()

# log_file = "log_" + str(time.clock_gettime(1)).split(".")[0] + ".log"
log_file = "log.log"

logging.basicConfig(filename=log_file, filemode='w',
                    format='[%(asctime)s] %(message)s',
                    level=getattr(logging, args.log_level.upper()))

if len(sys.argv) == 1:
    print("You didn't give any arguments\n"
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
    print("you didn't give an input graph file")
    parser.print_help()
    sys.exit(0)

if args.k_mer == 0:
    print("WARNING! You did not give a k value."
          "The output statistics might not be accurate\n"
          "If the graph is bluntified ignore this warning.")

####################### gamdigest
if args.subcommands == "gamdigest":
    if args.gam_file is not None:
        if args.pickle_out is not None:
            logging.info("reading gam file and building dict")
            all_reads = digest_gam(args.in_graph, args.gam_file, args.pickle_out)
            logging.info("finished successfully")
            sys.exit()
        else:
            print("You did not provide a path for the pickled dictionary output")
    else:
        print("Please provide the path to the gam file")
        sys.exit(1)

####################### compact graph
if args.subcommands == "compact":
    if args.compacted is not None:
        logging.info("Reading Graph...")

        if args.k_mer == 0:
            graph = Graph(args.in_graph, 1, args.coverage)
        else:
            graph = Graph(args.in_graph, args.k_mer, coverage=args.coverage)
        logging.info("Compacting Graph...")
        # pdb.set_trace()
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
            graph = Graph(args.in_graph, 1, args.coverage)
        else:
            graph = Graph(args.in_graph, args.k_mer, coverage=args.coverage)
        logging.info("Finding Biggest Component...")
        biggest_comp = graph.biggest_comp()
        print("Writing Biggset Component...")
        graph.write_graph(output_file=args.biggest_comp, set_of_nodes=biggest_comp)
        logging.info("Done...")
    else:
        print("Please provide the path for the biggest component graph")
        sys.exit(1)

####################### Bubbles
if args.subcommands == "bchains":
    # output_file = args.out_bubbles
    logging.info("Reading Graph...")
    if args.k_mer == 0:
        graph = Graph(args.in_graph, 1, args.coverage)
    else:
        graph = Graph(args.in_graph, args.k_mer, coverage=args.coverage)

    if args.bubbles:
        # print("[{}] Compacting graph...".format(current_time()))
        # graph.compact()
        logging.info("Finding chains...")
        graph.find_chains(only_simple=args.only_simple)
        graph.fill_bubble_info()
        logging.info("Done finding chains...")
        print("Sequence coverage of the bubble chains is {}%".format(graph.chain_cov_seq()))
        print("Node coverage of the bubble chains is {}%".format(graph.chain_cov_node()))
        b_numbers = graph.bubble_number()
        print("The number of Simple Bubbles is {}\n"
              "The number of Superbubbles is {}\n"
              "The number of insertions is {}".format(b_numbers[0], b_numbers[1],
                                                      b_numbers[2]))
        print("The longest chain seq-wise has {} bp".format(graph.longest_chain_seq().length_seq(graph.k)))
        print("The longest chain bubble_wise has {} bubbles".format(len(graph.longest_chain_bubble())))

        if args.out_haplos:
            logging.info("Outputting two random haplotypes of each bubble chain...")
            output_chains_fasta(graph)

        if args.out_fasta is not None:
            logging.info("Outputting each bubble branch...")
            write_fasta(args.out_fasta, graph)

        if args.chains_gfa is not None:
            logging.info("Outputting bubble chains gfa...")
            graph.write_b_chains(output=args.chains_gfa)

        if args.out_json is not None:
            logging.info("Outputting bubble chains gfa...")
            # todo
            # graph.write_chains_json(output=args.graph_out)

####################### BFS
if args.subcommands == "bfs":
    if args.starting_nodes is not None:
        if args.bfs_len is not None:
            if args.output_neighborhood is not None:

                logging.info("Reading Graph...")
                if args.k_mer == 0:
                    graph = Graph(args.in_graph, 1)
                else:
                    graph = Graph(args.in_graph, args.k_mer)

                for n in args.starting_nodes:
                    logging.info("extracting neighborhood around node {}".format(n))
                    set_of_nodes = bfs(graph, n, args.bfs_len)
                    graph.write_graph(set_of_nodes=set_of_nodes,
                                      output_file=args.output_neighborhood, append=True, modified=True)
                    logging.info("finished successfully...")
            else:
                print("You need to give an output file name --output_neighborhood")
                sys.exit()
        else:
            print("You did not give the neighborhood size")
            sys.exit(1)
    else:
        print("You did not give the starting node(s)")

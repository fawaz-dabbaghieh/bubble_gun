import sys
import argparse
import logging
from BubbleGun.bfs import bfs
from BubbleGun.Graph import Graph
from BubbleGun.bubbles_fasta import write_bubbles
from BubbleGun.find_bubbles import find_bubbles
from BubbleGun.fasta_chains import output_chains_fasta
from BubbleGun.json_out import json_out
from BubbleGun.output_certain_chains import write_certain_chains
from BubbleGun.connect_bubbles import connect_bubbles
from BubbleGun.find_parents import find_parents

parser = argparse.ArgumentParser(description='Find Bubble Chains.', add_help=True)
subparsers = parser.add_subparsers(help='Available subcommands', dest="subcommands")

parser._positionals.title = 'Subcommands'
parser._optionals.title = 'Global Arguments'

########################## general commands ###############################

parser.add_argument("-g", "--in_graph", metavar="GRAPH_PATH", dest="in_graph",
                    default=None, type=str, help="graph file path (GFA or VG)")

parser.add_argument("-v", "--version", action="store_true",
                    help="outputs version")

parser.add_argument("--log_file", dest="log_file", type=str, default="log.log",
                        help="The name/path of the log file. Default: log.log")

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

# ########################## Digest gam ###############################
# gam_parser = subparsers.add_parser('gamdigest', help='Command for digesting a gam file')
#
# gam_parser.add_argument("--json_file", dest="json_file", metavar="JSON_FILE",
#                         type=str, default=None, help="The JSON file wtih bubble chains information")
#
# gam_parser.add_argument("--alignment_file", dest="gam_file", metavar="GAM",
#                         type=str, default=None, help="Take GAM file and output pickled dict")
#
# gam_parser.add_argument("--min_cutoff", dest="min_cutoff", type=int, default=None,
#                         help="The minimum cutoff of a mapping length.")
#
# gam_parser.add_argument("--out_dict", dest="pickle_out",
#                         type=str, default=None,
#                         help="A pickled dictionary output path. contains read_id:[nodes]")

########################## output chain ###############################
output_chain = subparsers.add_parser('chainout', help='Outputs certain chain(s) given by their id as a GFA file')
output_chain.add_argument("--json_file", dest="json_file", metavar="JSON_FILE",
                          type=str, default=None, help="The JSON file wtih bubble chains information")

output_chain.add_argument("--chain_ids", dest="chain_ids", metavar="CHAIN_IDS", type=str, nargs="+",
                          default=None, help="Give the chain Id(s) to be outputted")

output_chain.add_argument("--output_chain", dest="output_chain", metavar="OUTPUT",
                          type=str, default=None, help="Output path for the chains chosen")

args = parser.parse_args()
if args.version:
    from BubbleGun.__version__ import version
    print(f"bubblegun version {version}")
    sys.exit(0)

# log_file = "log_" + str(time.clock_gettime(1)).split(".")[0] + ".log"
log_file = args.log_file

logging.basicConfig(filename=log_file, filemode='w',
                    format='[%(asctime)s] %(message)s',
                    level=getattr(logging, args.log_level.upper()))

logging.info(" ".join(["argument given:"] + sys.argv))



def main():
    if len(sys.argv) == 1:
        print("You did not provide any arguments\n"
              "Try to use -h or --help for help\n")
        sys.exit()

    if args.subcommands is None:
        print("Please provide a subcommand after the global commands")
        sys.exit(1)

    if args.in_graph is None:
        print("You need to provide an input graph with -g")
        sys.exit(1)
    # if args.in_graph is None:
    #     if args.subcommands != "gamdigest":
    #         print("you didn't give an input graph file")
    #         parser.print_help()
    #         sys.exit(0)

    ####################### chainout
    if args.subcommands == "chainout":
        if args.json_file is not None:
            if args.chain_ids is not None:
                if args.output_chain is not None:

                    logging.info("Reading Graph...")
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

    # ####################### gamdigest
    # if args.subcommands == "gamdigest":
    #     if args.gam_file is not None:
    #         if args.pickle_out is not None:
    #             if args.min_cutoff is not None:
    #                 logging.info("reading gam file and building dict")
    #                 all_reads = digest_gam(args.in_graph, args.gam_file, args.min_cutoff, args.pickle_out)
    #                 logging.info("finished successfully")
    #                 # sys.exit()
    #             else:
    #                 print("You did not provide the minimum cutoff. Maybe something like 3 times the k-mer length")
    #                 sys.exit(1)
    #         else:
    #             print("You did not provide a path for the pickled dictionary output")
    #             sys.exit(1)
    #     else:
    #         print("Please provide the path to the gam file")
    #         sys.exit(1)

    ####################### compact graph
    if args.subcommands == "compact":
        if args.compacted is not None:
            logging.info("Reading Graph...")
            graph = Graph(args.in_graph)

            logging.info("Compacting Graph...")
            graph.compact()
            logging.info("Writing Compacted Graph...")
            graph.write_graph(output_file=args.compacted, optional_info=False)
            logging.info("Done...")
        else:
            print("Please provide the path for the output compacted graph")
            sys.exit(1)

    ####################### biggest component
    if args.subcommands == "biggestcomp":
        if args.biggest_comp is not None:
            logging.info("Reading Graph...")

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
        if (args.low_memory and (args.out_fasta is not None)) or (args.low_memory and (args.chains_gfa is not None)):
            print("You cannot combine memory saving with --fasta or --chains_gfa")
            sys.exit(0)

        if args.out_haplos:
            if args.low_memory:
                print("You cannot have save memory and output haplos")
                sys.exit()
            if not args.only_simple:
                print("If you want 2 haplotyhpes out, then you need to choose --only_simple")
                sys.exit()
            if args.only_super:
                print("You cannot have out haplotypes and both only_simple and only_super, only works with only_simple")
                sys.exit()

        logging.info("Reading Graph...")
        graph = Graph(args.in_graph, low_memory=args.low_memory)

        logging.info("Finding bubbles...")

        find_bubbles(graph, only_simple=args.only_simple, only_super=args.only_super)

        logging.info("Connecting bubbles...")
        # connecting individual bubbles into chains
        connect_bubbles(graph)

        # add information related to nested bubbles
        logging.info("Finding nested information...")
        find_parents(graph)

        logging.info("Done finding chains...")
        b_numbers = graph.bubble_number()
        print("The number of Simple Bubbles is {}\n"
              "The number of Superbubbles is {}\n"
              "The number of insertions is {}".format(b_numbers[0], b_numbers[1],
                                                      b_numbers[2]))

        if (0,0,0) != (b_numbers[0], b_numbers[1],b_numbers[2]):

            if not args.low_memory:
                print("Sequence coverage of the bubble chains is {}%".format(graph.chain_cov_seq()))
                print("Node coverage of the bubble chains is {}%".format(graph.chain_cov_node()))
                print("The longest chain seq-wise has {} bp".format(graph.longest_chain_seq().length_seq()))
                print("The longest chain bubble_wise has {} bubbles".format(len(graph.longest_chain_bubble())))
            if args.out_json is not None:
                logging.info("Outputting bubble chains gfa...")
                json_out(graph, args.out_json)

            if args.chains_gfa is not None:
                if args.low_memory:
                    print("You cannot have low memory and output GFA file of chains")
                    sys.exit()

                logging.info("Outputting bubble chains gfa...")
                graph.write_b_chains(output=args.chains_gfa)

            if args.out_fasta is not None:
                if args.low_memory:
                    print("You cannot have low memory and output fasta")
                    sys.exit()

                logging.info("Outputting each bubble branch...")
                write_bubbles(graph, args.out_fasta)

            if args.out_haplos:
                logging.info("Outputting two random haplotypes of each bubble chain...")
                output_chains_fasta(graph)

    ####################### BFS
    if args.subcommands == "bfs":
        if args.starting_nodes is not None:
            if args.bfs_len is not None:
                if args.output_neighborhood is not None:

                    logging.info("Reading Graph...")
                    graph = Graph(args.in_graph)

                    for n in args.starting_nodes:
                        logging.info("extracting neighborhood around node {}".format(n))
                        set_of_nodes = bfs(graph, n, args.bfs_len)
                        if not graph.compacted:
                            graph.write_graph(set_of_nodes=set_of_nodes,
                                              output_file=args.output_neighborhood, append=True, optional_info=True)
                        else:
                            graph.write_graph(set_of_nodes=set_of_nodes,
                                              output_file=args.output_neighborhood, append=True, optional_info=False)
                        logging.info("finished successfully...")
                else:
                    print("You need to give an output file name --output_neighborhood")
                    sys.exit()
            else:
                print("You did not give the neighborhood size")
                sys.exit(1)
        else:
            print("You did not give the starting node(s)")
        logging.info("Done...")

if __name__ == "__main__":
    main()

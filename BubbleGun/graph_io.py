import os
import sys
from BubbleGun.Node import Node
import logging


def write_gfa(graph, set_of_nodes=None,
              output_file="output_file.gfa", append=False, optional_info=False):
    """
    Write a gfa out

    :param graph: the graph object
    :param set_of_nodes: A list of node ids of the path or nodes we want to generate a GFA file for.
    :param output_file: path to output file
    :param append: if I want to append to a file instead of rewriting it
    :param optional_info: If set to True, all optional columns for S lines are outputted as well
    :return: writes a gfa file
    """
    nodes = graph.nodes

    if set_of_nodes is None:
        set_of_nodes = graph.nodes.keys()

    if append is False:
        f = open(output_file, "w+")
    else:
        if os.path.exists(output_file):
            f = open(output_file, "a")
        else:
            logging.warning("Trying to append to a non-existent file\n"
                            "creating an output file")
            f = open(output_file, "w+")

    for n1 in set_of_nodes:
        if n1 not in nodes:
            logging.warning("Node {} does not exist in the graph, skipped in output".format(n1))
            continue

        line = str("\t".join(("S", str(n1), nodes[n1].seq, "LN:i:" + str(nodes[n1].seq_len))))
        if optional_info:
            line += "\t" + nodes[n1].optional_info

        f.write(line + "\n")

        # writing edges
        edges = []
        # overlap = str(graph.k - 1) + "M\n"

        for n in nodes[n1].start:
            overlap = str(n[2]) + "M\n"
            # I am checking if the are nodes I want to write
            # I think I can remove this later as I implemented the .remove_node
            # to the Graph class that safely removes a node and all its edges
            # So there shouldn't be any edges to removed
            if n[0] in set_of_nodes:
                if n[1] == 0:
                    edge = str("\t".join(("L", str(n1), "-", str(n[0]), "+", overlap)))
                    edges.append(edge)
                else:
                    edge = str("\t".join(("L", str(n1), "-", str(n[0]), "-", overlap)))
                    edges.append(edge)

        for n in nodes[n1].end:
            overlap = str(n[2]) + "M\n"

            if n[0] in set_of_nodes:
                if n[1] == 0:
                    edge = str("\t".join(("L", str(n1), "+", str(n[0]), "+", overlap)))
                    edges.append(edge)
                else:
                    edge = str("\t".join(("L", str(n1), "+", str(n[0]), "-", overlap)))
                    edges.append(edge)

        for e in edges:
            f.write(e)

    f.close()


def write_chains(graph, output_file="output_bubble_chains.gfa", optional_info=False):
    """
    Write bubble chains as gfa file

    :param graph: graph object with bubble chains already detected
    :param output_file: output file path
    :param optional_info: If save memory was used then there are no sequence and this is set to False
    """
    nodes = graph.nodes
    f = open(output_file, "w+")
    set_of_nodes = set()
    # using a set so I do not write the same chains more once
    # in case this chains was a child of another chain
    # I probably can also check the chain's parent sb and parent chains id
    # if it's not 0 then I do not write it, if it is 0 then I write it
    for chain in graph.b_chains:
        for n in chain.list_chain():
            set_of_nodes.add(n)

    for n1 in set_of_nodes:
        # writing nodes in gfa file
        node = nodes[n1]

        if "LN" in nodes[n1].optional_info:
            line = str("\t".join(("S", str(n1), nodes[n1].seq)))
        else:
            line = str("\t".join(("S", str(n1), nodes[n1].seq, "LN:i:" + str(nodes[n1].seq_len))))
        if optional_info:
            line += "\t" + nodes[n1].optional_info

        f.write(line + "\n")
        # writing edges
        edges = []

        for n in node.start:
            # I check if the neighbor belongs to the same chain
            # otherwise I don't write that edge
            if n[0] in set_of_nodes:
                overlap = str(n[2]) + "M\n"
                if n[1] == 0:
                    edge = str("\t".join(("L", str(n1), "-", str(n[0]), "+", overlap)))
                    edges.append(edge)
                else:
                    edge = str("\t".join(("L", str(n1), "-", str(n[0]), "-", overlap)))
                    edges.append(edge)

        for n in nodes[n1].end:
            overlap = str(n[2]) + "M\n"
            if n[0] in set_of_nodes:
                if n[1] == 0:
                    edge = str("\t".join(("L", str(n1), "+", str(n[0]), "+", overlap)))
                    edges.append(edge)
                else:
                    edge = str("\t".join(("L", str(n1), "+", str(n[0]), "-", overlap)))
                    edges.append(edge)

        for e in edges:
            f.write(e)

    f.close()


def read_gfa(gfa_file_path, low_memory=False):
    """
    Read a gfa file

    :param gfa_file_path: gfa graph file.
    :param low_memory: don't read the sequences to save memory
    :return: Dictionary of node ids and Node objects.
    """
    if not os.path.exists(gfa_file_path):
        logging.error("the gfa file path you gave does not exists, please try again!")
        sys.exit()

    nodes = dict()
    edges = []
    # min_node_length = k
    with open(gfa_file_path, "r") as lines:
        for line in lines:
            if line.startswith("S"):
                line = line.strip().split("\t")
                n_id = str(line[1])
                n_len = len(line[2])
                nodes[n_id] = Node(n_id)

                if len(line) > 3:  # save optional info
                    nodes[n_id].optional_info = "\t".join(line[3:])

                if not low_memory:
                    nodes[n_id].seq_len = n_len
                    nodes[n_id].seq = str(line[2]).strip()

            elif line.startswith("L"):
                edges.append(line)

    for e in edges:
        line = e.split()

        first_node = str(line[1])
        second_node = str(line[3])
        if first_node not in nodes:
            logging.warning(f"an edge between {first_node} and {second_node} exists but a "
                            f"node record for {first_node} does not exist in the file. Skipping")
            continue
        if second_node not in nodes:
            logging.warning(f"an edge between {first_node} and {second_node} exists but a "
                            f"node record for {second_node} does not exist in the file. Skipping")
            continue

        overlap = int(line[5][:-1])

        if line[2] == "-":
            from_start = True
        else:
            from_start = False

        if line[4] == "-":
            to_end = True
        else:
            to_end = False

        if from_start and to_end:  # from start to end L x - y -
            if (second_node, 1, overlap) not in nodes[first_node].start:
                nodes[first_node].start.add((second_node, 1, overlap))
            if (first_node, 0, overlap) not in nodes[second_node].end:
                nodes[second_node].end.add((first_node, 0, overlap))

        elif from_start and not to_end:  # from start to start L x - y +

            if (second_node, 0, overlap) not in nodes[first_node].start:
                nodes[first_node].start.add((second_node, 0, overlap))

            if (first_node, 0, overlap) not in nodes[second_node].start:
                nodes[second_node].start.add((first_node, 0, overlap))

        elif not from_start and not to_end:  # from end to start L x + y +
            if (second_node, 0, overlap) not in nodes[first_node].end:
                nodes[first_node].end.add((second_node, 0, overlap))

            if (first_node, 1, overlap) not in nodes[second_node].start:
                nodes[second_node].start.add((first_node, 1, overlap))

        elif not from_start and to_end:  # from end to end L x + y -
            if (second_node, 1, overlap) not in nodes[first_node].end:
                nodes[first_node].end.add((second_node, 1, overlap))

            if (first_node, 1, overlap) not in nodes[second_node].end:
                nodes[second_node].end.add((first_node, 1, overlap))

    # hacky fix for now
    for n in nodes.values():
        n.start = list(n.start)
        n.end = list(n.end)
    return nodes

# def read_vg(vg_file_path, k):
#     """
#     Read a vg file
#
#     :param vg_file_path: vg graph file.
#     :return: Dictionary of node ids and Node objects.
#     """
#     if not os.path.exists(vg_file_path):
#         logging.error("the vg file path you gave does not exist, please try again!")
#         sys.exit()
#
#     nodes = dict()
#     edges = []
#     min_node_length = k
#     with stream.open(vg_file_path, "rb") as in_stream:
#         for data in in_stream:
#             graph = BubbleGun.vg_pb2.Graph()
#             # import pdb
#             # pdb.set_trace()
#             graph.ParseFromString(data)
#
#             for n in graph.node:
#                 nodes[n.id] = Node(n.id)
#                 nodes[n.id].seq = str(n.sequence)
#                 nodes[n.id].seq_len = len(n.sequence)
#
#                 if min_node_length > nodes[n_id].seq_len:
#                     logging.error("Node {} has a sequence of length {}"
#                                   " which is smaller than the provided k\n"
#                                   "Not allowed.".format(nodes[n_id].id,
#                                                         nodes[n_id].seq_len))
#                     sys.exit()
#
#             for e in graph.edge:
#                 edges.append(e)
#
#     for e in edges:
#         k = getattr(e, "from")
#         neighbor = e.to
#         from_start = e.from_start
#         to_end = e.to_end
#
#         if from_start is True and to_end is True:  # from start to end L x - y -
#             nodes[k].start.append((neighbor, 1))
#             nodes[neighbor].end.append((k, 0))
#
#         elif from_start is True and to_end is False:  # from start to start L x - y +
#             nodes[k].start.append((neighbor, 0))
#             nodes[neighbor].start.append((k, 0))
#
#         elif from_start is False and to_end is False:  # from end to start L x + y +
#             nodes[k].end.append((neighbor, 0))
#             nodes[neighbor].start.append((k, 1))
#
#         elif from_start is False and to_end is True:  # from end to end L x + y -
#             nodes[k].end.append((neighbor, 1))
#             nodes[neighbor].end.append((k, 1))
#
#     return nodes

import os
import sys
from .Node import Node
import core.vg_pb2
import stream

def write_gfa(graph, set_of_nodes=None,
    output_file="output_file.gfa", append=False, modified=False):
    """
    Write a gfa out

    :param nodes: Dictionary of nodes object.
    :param set_of_nodes: A list of node ids of the path or nodes we want to generate a GFA file for.
    :param k: overlap between two nodes.
    :param output_file: path to output file
    :param append: if I want to append to a file instead of rewriting it
    :param modified: To write my modified GFA file format instead of the standard GFA
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
            print("the output file {} does not exist".format(output_file))
            return None

    for n1 in set_of_nodes:
        # writing nodes in gfa file
        if modified:
            node = nodes[n1]
            # todo for now I don't care to which sb the node belongs, I just care about simple bubbles for phasing
            specification = str(":".join((str(node.which_chain), str(0),
                                          str(node.which_b), str(node.which_allele))))
            if nodes[n1].seq == "":
                line = str("\t".join(("S", str(n1), str("A" * nodes[n1].seq_len), specification)))
            else:
                line = str("\t".join(("S", str(n1), nodes[n1].seq, specification)))

            f.write(line + "\n")
        else:
            if nodes[n1].seq == "":
                line = str("\t".join(("S", str(n1), str("A" * nodes[n1].seq_len))))
            else:
                line = str("\t".join(("S", str(n1), nodes[n1].seq)))

            f.write(line + "\n")

        # writing edges
        edges = []
        overlap = str(graph.k - 1) + "M\n"

        for n in nodes[n1].start:
            # I am checking if the are nodes I want to write
            # I think I can remove this later as I implemented the .remove_node
            # to the Graph class that safely removes a node and all its edgse
            # So there shouldn't be any edges to removed
            if n[0] in set_of_nodes:
                if n[1] == 0:
                    edge = str("\t".join(("L", str(n1), "-", str(n[0]), "+", overlap)))
                    edges.append(edge)
                else:
                    edge = str("\t".join(("L", str(n1), "-", str(n[0]), "-", overlap)))
                    edges.append(edge)

        for n in nodes[n1].end:
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


def write_chains(graph, output_file="output_bubble_chains.gfa"):
    """
    Write bubble chains as gfa file

    :param graph: graph object with bubble chains already detected
    :param output_file: otput file path
    """
    nodes = graph.nodes
    f = open(output_file, "w+")

    overlap = str(graph.k - 1) + "M\n"
    for chain in graph.b_chains:
        set_of_nodes = chain.list_chain()

        for n1 in set_of_nodes:
            # writing nodes in gfa file
            node = nodes[n1]
            # todo for now I don't care to which sb the node belongs
            # I just care about simple bubbles for phasing
            specification = str(":".join((str(node.which_chain), str(0),
                                          str(node.which_b), str(node.which_allele))))
            if node.seq == "":
                line = str("\t".join(("S", str(n1), str("A" * nodes[n1].seq_len), specification)))
            else:
                line = str("\t".join(("S", str(n1), nodes[n1].seq, specification)))

            f.write(line + "\n")
            # writing edges
            edges = []

            for n in node.start:
                # I check if the neighbor belongs to the same chain
                # otherwise I don't write that edge 
                if n[0] in set_of_nodes:
                    if n[1] == 0:
                        edge = str("\t".join(("L", str(n1), "-", str(n[0]), "+", overlap)))
                        edges.append(edge)
                    else:
                        edge = str("\t".join(("L", str(n1), "-", str(n[0]), "-", overlap)))
                        edges.append(edge)

            for n in nodes[n1].end:
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

def read_gfa(gfa_file_path, modified=False):
    """
    Read a gfa file

    :param gfa_file_path: gfa graph file.
    :param modified: if I'm reading my modified GFA with extra information for the nodes
    :return: Dictionary of node ids and Node objects.
    """
    if not os.path.exists(gfa_file_path):
        print("the gfa file path you gave does not exists, please try again!")
        sys.exit()

    nodes = dict()
    edges = []
    with open(gfa_file_path, "r") as lines:
        for line in lines:
            if line.startswith("S"):
                if modified:
                    line = line.split("\t")
                    n_id = int(line[1])
                    n_len = len(line[2])
                    nodes[n_id] = Node(n_id)
                    nodes[n_id].seq_len = n_len
                    nodes[n_id].seq = str(line[2])
                    specifications = str(line[3])
                    specifications = specifications.split(":")
                    nodes[n_id].which_chain = int(specifications[0])
                    nodes[n_id].which_sb = int(specifications[1])
                    nodes[n_id].which_b = int(specifications[2])
                    nodes[n_id].which_allele = int(specifications[3])

                else:

                    line = line.split()
                    n_id = int(line[1])
                    n_len = len(line[2])
                    nodes[n_id] = Node(n_id)
                    nodes[n_id].seq_len = n_len
                    nodes[n_id].seq = str(line[2])

            elif line.startswith("L"):
                edges.append(line)

    for e in edges:
        line = e.split()

        k = int(line[1])
        neighbor = int(line[3])
        if line[2] == "-":
            from_start = True
        else:
            from_start = False

        if line[4] == "-":
            to_end = True
        else:
            to_end = False

        if from_start is True and to_end is True:  # from start to end L x - y -
            if (neighbor, 1) not in nodes[k].start:
                nodes[k].start.append((neighbor, 1))
            if (k, 0) not in nodes[neighbor].end:
                nodes[neighbor].end.append((k, 0))

        elif from_start is True and to_end is False:  # from start to start L x - y +

            if (neighbor, 0) not in nodes[k].start:
                nodes[k].start.append((neighbor, 0))

            if (k, 0) not in nodes[neighbor].start:
                nodes[neighbor].start.append((k, 0))

        elif from_start is False and to_end is False:  # from end to start L x + y +
            if (neighbor, 0) not in nodes[k].end:
                nodes[k].end.append((neighbor, 0))

            if (k, 1) not in nodes[neighbor].start:
                nodes[neighbor].start.append((k, 1))

        elif from_start is False and to_end is True:  # from end to end L x + y -
            if (neighbor, 1) not in nodes[k].end:
                nodes[k].end.append((neighbor, 1))

            if (k, 1) not in nodes[neighbor].end:
                nodes[neighbor].end.append((k, 1))

    return nodes


def read_vg(vg_file_path):
    """
    Read a vg file
    
    :param vg_file_path: vg graph file.
    :return: Dictionary of node ids and Node objects.
    """
    if not os.path.exists(vg_file_path):
        print("the vg file path you gave does not exist, please try again!")
        sys.exit()

    nodes = dict()
    edges = []
    with stream.open(vg_file_path, "rb") as in_stream:
        for data in in_stream:
            graph = core.vg_pb2.Graph()
            # import pdb
            # pdb.set_trace()
            graph.ParseFromString(data)

            for n in graph.node:
                nodes[n.id] = Node(n.id)
                nodes[n.id].seq = str(n.sequence)
                nodes[n.id].seq_len = len(n.sequence)

            for e in graph.edge:
                edges.append(e)

    for e in edges:
        k = getattr(e, "from")
        neighbor = e.to
        from_start = e.from_start
        to_end = e.to_end

        if from_start is True and to_end is True:  # from start to end L x - y -
            nodes[k].start.append((neighbor, 1))
            nodes[neighbor].end.append((k, 0))

        elif from_start is True and to_end is False:  # from start to start L x - y +
            nodes[k].start.append((neighbor, 0))
            nodes[neighbor].start.append((k, 0))

        elif from_start is False and to_end is False:  # from end to start L x + y +
            nodes[k].end.append((neighbor, 0))
            nodes[neighbor].start.append((k, 1))

        elif from_start is False and to_end is True:  # from end to end L x + y -
            nodes[k].end.append((neighbor, 1))
            nodes[neighbor].end.append((k, 1))

    return nodes
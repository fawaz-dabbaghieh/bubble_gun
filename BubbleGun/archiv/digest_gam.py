import json
import logging
import stream
import pickle
from BubbleGun.vg_pb2 import Alignment
from BubbleGun.Graph import Graph


class Mapping:
    """
    contains information about mapping

    contains information such as the length of the mapping
    what nodes involved in this mapping and to which chain they belong to
    """
    __slots__ = ['nodes', 'chain', 'length']

    def __init__(self):
        self.nodes = []
        self.chain = 0
        self.length = 0

    def add_node(self, node_id, chain_id):
        if self.chain == 0:
            self.chain = chain_id
            self.nodes.append(node_id)

        elif self.chain != chain_id:
            logging.warning("Node {} does not belong to the same chain".format(node_id))
            # self.nodes.append(node.id)

        else:
            self.nodes.append(node_id)

    def fill_mapping(self, nodes, alignment, length):
        self.length = length
        for m in alignment.path.mapping:
            self.add_node(m.position.node_id, nodes[m.position.node_id])


class ReadMappings:

    def __init__(self, name):
        self.name = name
        self.mappings = []

    def check_add(self, mapping):
        # I am checking if it's a mapping to the same chain
        # if it is and it is longer, the previous one is removed and the new mapping is added
        for idx, m in enumerate(self.mappings):
            if m.chain == mapping.chain:
                if m.length > mapping.length:
                    return False
                else:
                    self.mappings.pop(idx)
                    return True
        return True

    def add_mapping(self, mapping):
        if self.check_add(mapping):
            self.mappings.append(mapping)

    def list_nodes(self):
        nodes = []
        for m in self.mappings:
            nodes += m.nodes
        return nodes

    def list_nodes_debug(self):
        nodes = []
        for m in self.mappings:
            nodes.append(m.nodes)
        return nodes


# def check_same_chain(list_of_nodes, nodes):

#     current_chain = nodes[list_of_nodes[0]].which_chain
#     for n in list_of_nodes:
#         if nodes[n].which_chain != current_chain:
#             print("problem with chain {}".format(nodes[n].which_chain))
#             print("list of nodes are {}".format(list_of_nodes))
#             sys.exit()

def build_reads_dict(nodes, gam_file_path, min_cutoff):
    all_reads = dict()

    # reading gam file
    with stream.open(str(gam_file_path), "rb") as in_stream:
        counter = 0
        read_mappings = ReadMappings(name="first")

        for data in in_stream:
            counter += 1

            if (counter % 10000000) == 0:
                logging.info("{} mappings processed".format(counter))

            align = Alignment()
            align.ParseFromString(data)

            # skipping alignments with less than minimum cutoff
            if len(align.sequence) < min_cutoff:
                continue

            if align.name not in all_reads:  # either first or new read
                mapping = Mapping()
                # mapping now has the nodes and the length
                mapping.fill_mapping(nodes, align, len(align.sequence))

                all_reads[align.name] = []
                # all_reads[align.name] = read_mappings

                if read_mappings.name == "first":  # only once for first read
                    # all_reads[align.name].name = align.name
                    read_mappings.name = align.name
                    read_mappings.add_mapping(mapping)
                    # all_reads[read_mappings.name].add_mapping(mapping)
                    # all_reads[align.name].add_mapping(mapping)

                # new read, need to store the previous read_mappings
                # in all_reads and start a new ReadMappings object to fill
                else:
                    # all_reads[align.name] = ReadMappings(name=align.name)
                    # all_reads[align.name].add_mapping(mapping)
                    all_reads[read_mappings.name] = read_mappings.list_nodes()
                    read_mappings = ReadMappings(name=align.name)
                    read_mappings.add_mapping(mapping)

            # this read already exists (from previous mapping)
            # add this mapping
            # add mapping checks if this mapping is a new chain or for a chain
            # already seen with this read, then compares the length and keep
            # the longer one
            else:
                mapping = Mapping()
                mapping.fill_mapping(nodes, align, len(align.sequence))

                read_mappings.add_mapping(mapping)
                # all_reads[align.name].add_mapping(mapping)

    return all_reads


def digest_gam(json_file, gam, min_cutoff, pickled_out):
    nodes = dict()
    logging.info("Reading JSON file...")
    with open(json_file, "r") as in_file:
        for line in in_file:
            chain = json.loads(line)
            for n in chain['ends']:
                nodes[n] = chain.id
            for bubble in chain['bubbles']:
                for n in bubble['ends']:
                    nodes[n] = chain.id
                for n in bubble['ends']:
                    nodes[n] = chain.id

    # graph = Graph(graph_file=gfa, modified=True)
    all_reads = build_reads_dict(nodes, gam, min_cutoff)

    logging.info("finished building dict, pickling it...")
    out_file = open(pickled_out, "ab")
    pickle.dump(all_reads, out_file)
    out_file.close()

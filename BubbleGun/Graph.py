from BubbleGun.graph_io import read_gfa, write_gfa, write_chains
from BubbleGun.compact_graph import compact_graph
from BubbleGun.connected_components import all_components
from BubbleGun.bfs import bfs
import sys
import os


class Graph:
    """
    Graph object containing the important information about the graph
    """

    __slots__ = ['nodes', 'b_chains', 'bubbles', 'compacted']

    def __init__(self, graph_file=None, low_memory=False):
        if graph_file is not None:
            if not os.path.exists(graph_file):
                print("graph file {} does not exist".format(graph_file))
                sys.exit()
            # loading nodes from file
            self.nodes = read_gfa(gfa_file_path=graph_file, low_memory=low_memory)
        else:
            self.nodes = dict()
        # elif graph_file.endswith(".vg"):
        #     self.nodes = read_vg(vg_file_path=graph_file, k=k, modified=modified, coverage=coverage)

        self.b_chains = set()  # list of BubbleChain objects
        self.bubbles = dict()
        self.compacted = False
        # self.k = 1

    def __len__(self):
        """
        overloading the length function
        """

        return len(self.nodes)

    def __str__(self):
        """
        overloading the string function for printing
        """

        return "The graph has {} Nodes and {} chains".format(
            len(self.nodes), len(self.b_chains))

    # def __repr__(self):
    #     """
    #     overloading the string function for printing
    #     """
    #     return "The graph has {} Nodes and {} bubble and {} chains".format(
    #         len(self.nodes), len(self.bubbles), len(self.b_chains))

    def add_chain(self, chain):
        """
        adds a bubble chain to the graph
        """
        if len(chain.sorted) == 0:
            chain.find_ends()
            chain.sort()
            if len(chain.ends) != 2:  # circular chains or other weird stuff
                nodes_set = set(chain.list_chain())
                self.write_graph(set_of_nodes=nodes_set, append=True,
                                 output_file="circular_and_other_problematic_chains.gfa", optional_info=False)

            else:
                # self.b_chains[chain._BubbleChain__key()] = chain
                if chain not in self.b_chains:
                    self.b_chains.add(chain)

    def total_seq_length(self):
        """
        returns total sequence length
        """
        total = 0
        for n in self.nodes.values():
            total += n.seq_len
        return total
        # total = 0
        # counted_overlap = set()
        # for n in self.nodes.values():
        #
        #     total += n.seq_len
        #     if n.id not in counted_overlap:
        #         counted_overlap.add(n.id)
        #
        #         for nn in n.end:
        #             counted_overlap.add(nn[0])
        #             total -= nn[2]
        #         for nn in n.start:
        #             counted_overlap.add(nn[0])
        #             total -= nn[2]
        #
        # return total

    def longest_chain_bubble(self):
        """
        returns the longest bubble chain bubble wise
        In case there are more than one longest chain it
        returns the first one found
        """

        lengths_list = [len(x) for x in self.b_chains]
        m = max(lengths_list)
        m_idx = lengths_list.index(m)
        return list(self.b_chains)[m_idx]

    def longest_chain_seq(self):
        """
        returns the longest bubble chain sequence wise
        In case there are more than on longest chain it
        returns the first one found
        """

        lengths_list = [x.length_seq() for x in self.b_chains]
        m = max(lengths_list)
        m_idx = lengths_list.index(m)
        # returning only one chain that is the max, there could be a tie
        return list(self.b_chains)[m_idx]

    def nodes_in_chains(self):
        """
        returns the set of all nodes in bubble chains
        """
        # pdb.set_trace()
        all_nodes = []
        for chain in self.b_chains:
            all_nodes += chain.list_chain()
        return set(all_nodes)

    def seq_in_chains(self):
        """
        returns how much sequence their are in the bubble chains
        """
        # total_length = 0
        # for chain in self.b_chains:
        #     chain_length = 0
        #     counted_overlap = set()
        #     chain_nodes = set(chain.list_chain(ids=False))
        #     for n in chain_nodes:
        #         chain_length += n.seq_len
        #         if n.id not in counted_overlap:
        #             counted_overlap.add(n.id)
        #             for nn in n.end:
        #                 if nn in chain_nodes:
        #                     counted_overlap.add(nn[0])
        #                     chain_length -= nn[2]
        #             for nn in n.start:
        #                 if nn in chain_nodes:
        #                     counted_overlap.add(nn[0])
        #                     chain_length -= nn[2]
        #     total_length += chain_length
        # return total_length
        s_in_c = 0
        for chain in self.b_chains:
            # if chain not in self.child_parent:
            s_in_c += chain.length_seq()
        return s_in_c

    def chain_cov_node(self):
        """
        returns the percentage the nodes in chains covered
        """
        # pdb.set_trace()
        n_in_c = self.nodes_in_chains()
        return float((len(n_in_c) * 100) / len(self.nodes))

    def chain_cov_seq(self):
        """
        returns the percentage the sequences in chains covered
        """
        chains_nodes = set()
        for chain in self.b_chains:
            for n in chain.list_chain():
                chains_nodes.add(n)
        total_seq = 0
        for n in chains_nodes:
            total_seq += self.nodes[n].seq_len
        return (total_seq*100) / float(self.total_seq_length())

    def num_single_bubbles(self):
        """
        return the number of chains that has only one bubble
        """

        nsb = 0
        for chain in self.b_chains:
            if len(chain) == 1:
                nsb += 1
        return nsb

    def reset_visited(self):
        """
        resets all nodes.visited to false
        """

        for n in self.nodes.values():
            n.visited = False

    def bubble_number(self):
        """
        returns a list of 3 counters, bubbles, superbubbles and insertions
        """

        counter = [0, 0, 0]
        for chain in self.b_chains:
            for b in chain.bubbles:
                if b.is_simple():
                    counter[0] += 1
                elif b.is_super():
                    counter[1] += 1
                elif b.is_insertion():
                    counter[2] += 1

        return counter

    # def find_chains(self, only_simple=False):
    #     """
    #     calls the find bubbles and chains algorithms
    #     then adds the objects to the graph
    #     """
    #
    #     find_bubble_chains(self, only_simple)

    def remove_node(self, n_id):
        """
        remove a node and its corresponding edges
        """
        starts = [x for x in self.nodes[n_id].start]
        for n_start in starts:
            overlap = n_start[2]
            if n_start[1] == 1:
                self.nodes[n_start[0]].end.remove((n_id, 0, overlap))
            else:
                self.nodes[n_start[0]].start.remove((n_id, 0, overlap))

        ends = [x for x in self.nodes[n_id].end]
        for n_end in ends:
            overlap = n_end[2]
            if n_end[1] == 1:
                self.nodes[n_end[0]].end.remove((n_id, 1, overlap))
            else:
                self.nodes[n_end[0]].start.remove((n_id, 1, overlap))

        del self.nodes[n_id]

    def remove_lonely_nodes(self):
        """
        remove singular nodes with no neighbors
        """

        nodes_to_remove = [n.id for n in self.nodes.values() if len(n.neighbors()) == 0]

        for i in nodes_to_remove:
            self.remove_node(i)

    def compact(self):
        """
        compact the unipaths in the graph
        and turns the graph into a compacted one
        """

        # if self.k == 0:
        #     logging.warning("if this is De Bruijn Graph"
        #                     " and you did not specify the k value"
        #                     " the compacting might not be correct, as overlaps"
        #                     " needs to be removed")
        compact_graph(self)
        self.compacted = True

    def write_graph(self, set_of_nodes=None,
                    output_file="output_graph.gfa",
                    append=False, optional_info=True):
        """writes a graph file as GFA

        list_of_nodes can be a list of node ids to write
        ignore_nodes is a list of node ids to not write out
        if append is set to true then output file should be an existing
        graph file to append to
        modified to output a modified graph file
        """
        if not output_file.endswith(".gfa"):
            output_file += ".gfa"

        write_gfa(self, set_of_nodes=set_of_nodes, output_file=output_file,
                  append=append, optional_info=optional_info)

    def write_b_chains(self, output="bubble_chains.gfa"):
        """writes bubble gains to a GFA file

        :params output: output file path
        """
        if not output.endswith(".gfa"):
            output += ".gfa"

        if self.compacted:
            write_chains(self, output_file=output, optional_info=False)
        else:
            write_chains(self, output_file=output, optional_info=True)

    def biggest_comp(self):
        """
        returns a list of sets for each component and the node ids in that
        component.
        """
        all_comp = all_components(self)
        lengths = [len(i) for i in all_comp]
        return all_comp[lengths.index(max(lengths))]

    def bfs(self, start, size):
        """
        Returns a neighborhood of size given around start node

        :param start: starting node for the BFS search
        :param size: size of the neighborhood to return
        """

        neighborhood = bfs(self, start, size)
        return neighborhood

    def fill_bubble_info(self):
        # chains_to_remove = set()
        b_counter = 0
        chain_num = 0
        for chain in self.b_chains:
            chain_num += 1  # To start from 1

            for bubble in chain.sorted:
                b_counter += 1
                if bubble.is_simple():
                    # randomly assigning which branch is zero and which is 1
                    # simple bubble only has 2 nodes inside, so 0 and 1
                    for allele, node in enumerate(bubble.inside):
                        # check if it hasn't been processed yet
                        # it might be a nested bubble inside an SB
                        # so don't need to change the tags then
                        # SB takes precedence
                        if node.which_chain == 0:
                            node.which_allele = allele
                            node.which_chain = chain_num
                            node.which_b = b_counter

                    # assigning the ends of the bubble to which chain
                    if bubble.source.which_chain == 0:
                        bubble.source.which_chain = chain_num

                    if bubble.sink.which_chain == 0:
                        bubble.sink.which_chain = chain_num

                else:  # superbubbles or insertions
                    for node in bubble.list_bubble():
                        # inside the SB it gets reset
                        self.nodes[node].which_b = 0
                        self.nodes[node].which_allele = -1
                        self.nodes[node].which_sb = b_counter
                        self.nodes[node].which_chain = chain_num

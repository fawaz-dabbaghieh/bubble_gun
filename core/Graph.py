from .graph_io import read_gfa, read_vg, write_gfa
from .find_bubbles import find_bubbles
from .compact_graph import compact_graph
from .connected_components import all_components


class Graph:
    """
    Graph object containing the important information about the graph
    """

    def __init__(self, graph_file):
        # loading nodes from file
        if graph_file.endswith(".gfa"):
            self.nodes = read_gfa(graph_file)
        elif graph_file.endswith(".vg"):
            self.nodes = read_vg(graph_file)

        self.b_chains = []  # list of BubbleChain objects
        self.bubbles = set()
        self.k = 1

    def __len__(self):
        """
        overloading the length function
        """

        return (len(self.nodes))

    def __str__(self):
        """
        overloading the string function for printing
        """

        return "The graph has {} Nodes and {} bubble and {} chains".format(
            len(self.nodes), len(self.bubbles), len(self.b_chains))

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

        self.b_chains.append(chain)

    def total_seq_length(self):
        """
        returns total sequence length
        """

        total = 0
        for n in self.nodes.values():
            total += n.seq_len - self.k
        return total

    def longest_chain_node(self):
        """
        returns the longest bubble chain bubble wise
        In case there are more than one longest chain it
        returns the first one found
        """

        lengths_list = [x.node_length() for x in self.b_chains]
        m = max(lengths_list)
        return self.b_chains[[i for i, j in enumerate(lengths_list) if j == m][0]]

    def longest_chain_seq(self):
        """
        returns the longest bubble chain sequence wise
        In case there are more than on longest chain it
        returns the first one found
        """

        lengths_list = [x.seq_length(k=self.k) for x in self.b_chains]
        m = max(lengths_list)
        return self.b_chains[[i for i, j in enumerate(lengths_list) if j == m][0]]

    def nodes_in_chains(self):
        """
        returns the set of all nodes in bubble chains
        """

        all_nodes = []
        for chain in self.b_chains:
            all_nodes += chain.list_chain()

        return set(all_nodes)

    def seq_in_chains(self):
        """
        returns how much sequence ther are in the bubble chains
        """

        s_in_c = 0
        for chain in self.b_chains:
            s_in_c += chain.seq_length(k=self.k)

        return s_in_c

    def chain_cov_node(self):
        """
        returns the percentage the nodes in chains covered
        """

        n_in_c = self.nodes_in_chains()
        return float((len(n_in_c)*100)/len(self.nodes))

    def chain_cov_seq(self):
        """
        returns the percentage the sequences in chains covered
        """

        s_in_c = self.seq_in_chains()

        return float((s_in_c*100)/self.total_seq_length())

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
        resets all nodes.visited to flase
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

    def find_chains(self):
        """
        calls the find bubbles and chains algorithms
        then adds the objects to the graph
        """

        find_bubbles(self)

    def remove_node(self, n_id):
        """
        remove a node and its corrisponding edges
        """

        for n_start in self.nodes[n_id].start:
            if n_start[1] == 1:
                self.nodes[n_start[0]].end.remove((n_id, 0))
            else:
                self.nodes[n_start[0]].start.remove((n_id, 0))

        for n_end in self.nodes[n_id].end:
            if n_end[1] == 1:
                self.nodes[n_end[0]].end.remove((n_id, 1))
            else:
                self.nodes[n_end[0]].start.remove((n_id, 1))

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

        if self.k == 0:
            print("WARNING! WARNING! if this is De Bruijn Graph"
                  " and you did not specify the k value"
                  " the compacting might not be correct, as overlaps"
                  " needs to be removed")
        compact_graph(self)

    def write_graph(self, set_of_nodes=None,
    output_file="output_graph.gfa", append=False, modified=False):
        """writes a graph file as GFA

        list_of_nodes can be a list of node ids to write
        ignore_nodes is a list of node ids to not write out
        if append is set to true then output file should be an existing
        graph file to append to
        modified to output a modified graph file
        """

        write_gfa(self, set_of_nodes=set_of_nodes, output_file=output_file,
            append=append, modified=modified)

    def write_b_chains(self, output="bubble_chains.gfa"):
        """writes bubble gains to a GFA file

        :params output: output file path
        """
        if not output.endswith(".gfa"):
            output += ".gfa"

        set_of_nodes = self.nodes_in_chains()
        write_gfa(self, set_of_nodes=set_of_nodes, output_file=output,
            append=False, modified=False)

    def components(self):
        return all_components(self)

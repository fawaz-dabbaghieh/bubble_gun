class BubbleChain:
    """
    BubbleChain object which is a set of bubbles
    """

    def __init__(self):
        self.bubbles = set()

    def __len__(self):
        """
        overloading the length function
        """
        return len(self.bubbles)

    def __contains__(self, item):
        """
        Overloading membership operator
        """
        if item in self.bubbles:
            return True
        return False

    # def __getitem__(self, index):
    #     """
    #     to make it support indexing
    #     """
    #     return self.bubbles[index]

    # def __setitem__(self, index, value):
    #     """
    #     for indexing support
    #     """
    #     self.bubbles[index] = value

    def add_bubble(self, bubble):
        """
        adds a bubble object to the chain
        """
        self.bubbles.add(bubble)

    def list_chain(self):
        """
        return all nodes in the chain as a list of node objects
        """
        c_list = []
        for b in self.bubbles:
            c_list += [b.source.id, b.sink.id] + [x.id for x in b.inside]
        return list(set(c_list))  # set to remove redundant sources and sinks

    def node_length(self):
        """
        returns how many nodes there are in the chain
        """
        return len(self.list_chain())

    def seq_length(self, k):
        """
        returns sequence length covered by the chain
        """
        c_list = []
        for b in self.bubbles:
            c_list += [b.source, b.sink] + b.inside
        c_list = list(set(c_list))

        total_seq = 0
        for n in c_list:
            total_seq += n.seq_len - k
        return total_seq

    def find_ends(self):
        """
        returns the ends of the chain as node IDs
        """
        ends = []
        all_ends = []
        for b in self.bubbles:
            all_ends.append(b.source.id)
            all_ends.append(b.sink.id)
        for n in all_ends:
            if all_ends.count(n) == 1:
                ends.append(n)
        return ends

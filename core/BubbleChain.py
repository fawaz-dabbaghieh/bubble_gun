from collections import Counter

class BubbleChain:
    """
    BubbleChain object which is a set of bubble objects
    """
    def __init__(self):
        """
        initialize the BubbleChain as a set of bubble
        """
        self.bubbles = set()
        self.ends = []

    def __len__(self):
        """
        overloading the length function
        """
        return len(self.bubbles)

    def __contains__(self, item):
        """
        Overloading membership operator
        """
        return item in self.bubbles

    def add_bubble(self, bubble):
        """
        adds a bubble object to the chain
        """
        self.bubbles.add(bubble)

    def list_chain(self, ids=True):
        """
        return all nodes in the chain as a list of node objects
        """
        c_list = []
        for b in self.bubbles:
            c_list += [b.source, b.sink] + b.inside
        if ids:
            return list(set([x.id for x in c_list]))

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
        # c_list = []
        # for b in self.bubbles:
        #     c_list += [b.source, b.sink] + b.inside
        # c_list = list(set(c_list))

        total_seq = 0
        for n in self.list_chain(ids=False):
            total_seq += n.seq_len - k
        return total_seq

    def find_ends(self):
        """
        returns the ends of the chain as node IDs
        """
        all_ends = []
        for b in self.bubbles:
            all_ends += [b.source.id, b.sink.id]
        
        # looks at all the sources,sinks of the bubbles in the chain
        # only the ends of the chain should have a count of 1
        # the rest are counted twice as two adjacent bubbles will share
        # the same node as sink for one and source for the other
        self.ends = [k for k, v in Counter(all_ends).items() if v == 1]

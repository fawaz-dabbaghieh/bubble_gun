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
        self.sorted = []  # sorted bubble pointers
        self.ends = []  # node ids of the chain ends

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

    def length_node(self):
        """
        returns how many nodes there are in the chain
        """
        return len(self.list_chain())

    def length_seq(self, k):
        """
        returns sequence length covered by the chain
        """
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


    def sort(self):
        # I couldn't sort the set of bubbles (overload a bigger than function
        # in Bubble to use for the python sort function) because the sorting
        # here is based on the chain and the ends of the chain
        # I don't know before hand which bubble is "bigger" or "smaller" than
        # the other bubble until I have the complete chain
        # for example, if I start traversing from the middle of the chain
        # looking "left" or "right" I still don't know who's is "bigger"
        # until I finish the whole chain.

        # The hacky way to do it then is to have a list of bubble pointers
        # sorted based on which end of the chain I chose as the start 
        # of the chain
        if len(self.ends) == 0:
            self.find_ends()
            
        start = self.ends[0]  # randomly choosing one end of the cahin as start
        while len(self.sorted) < len(self):
            for b in self.bubbles:
                b_ends = [b.source.id, b.sink.id]
                if b in self.sorted:
                    continue
                if start in b_ends:
                    b_ends.pop(b_ends.index(start))
                    start = b_ends[0]
                    self.sorted.append(b)

from collections import Counter


class BubbleChain:
    """
    BubbleChain object which is a set of bubble objects
    """
    __slots__ = ['bubbles', 'sorted', 'ends', 'key', 'id', 'parent_chain', 'parent_sb']

    def __init__(self):
        """
        initialize the BubbleChain as a set of bubble
        """
        self.bubbles = set()
        self.sorted = []  # sorted bubble pointers
        self.ends = []  # node ids of the chain ends
        self.id = 0
        self.parent_sb = 0
        self.parent_chain = 0
        # self.key = self.__hash__()

    def __key(self):
        """
        calculated the key of the bubble chain
        """
        if self.ends[0] > self.ends[1]:
            return self.ends[0], self.ends[1]
        return self.ends[1], self.ends[0]

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return self.__key() == other.__key()

    def __ne__(self, other):
        return not self.__eq__(other)

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

    def length_seq(self):
        """
        returns sequence length covered by the chain
        """
        # total_seq = 0
        # counted_overlaps = set()
        # for n in self.list_chain(ids=False):
        #     total_seq += n.seq_len
        #     if n.id not in counted_overlaps:
        #         for nn in n.end:
        #             counted_overlaps.add(nn[0])
        #             total_seq -= nn[2]
        #         for nn in n.start:
        #             counted_overlaps.add(nn[0])
        #             total_seq -= nn[2]
        total_seq = 0
        for n in self.list_chain(ids=False):
            total_seq += n.seq_len
        return total_seq

    def find_ends(self):
        """
        Find the ends of a chain

        todo maybe add the ends while constructing the chain in find_sb_alg
        """
        self.ends = [k for k, v in Counter([b.source.id for b in self.bubbles] + [b.sink.id for b in self.bubbles]).items() if v == 1]

    def sort(self):
        """
        sorts the bubbles in the chain
        """
        # finding ends
        all_ends = dict()
        for b in self.bubbles:
            source = str(b.source.id)
            sink = str(b.sink.id)
            if source > sink:
                all_ends[(source, sink)] = b
            else:
                all_ends[(sink, source)] = b

            # looks at all the sources, sinks of the bubbles in the chain
            # only the ends of the chain should have a count of 1
            # the rest are counted twice as two adjacent bubbles will share
            # the same node as sink for one and source for the other
        # if len(self.ends) == 0:
        #     self.ends = [k for k, v in Counter([n for sublist in all_ends.keys() for n in sublist]).items() if v == 1]
        # try:
        #     assert len(self.ends) == 2
        # except AssertionError:
        #     pdb.set_trace()
        # I couldn't sort the set of bubbles (overload a "bigger than" function
        # in Bubble to use for the python sort function) because the sorting
        # here is based on the chain and the ends of the chain
        # I don't know before hand which bubble is "bigger" or "smaller" than
        # the other bubble until I have the complete chain
        # for example, if I start traversing from the middle of the chain
        # looking "left" or "right" I still don't know who's is "bigger"
        # until I finish the whole chain.
        # pdb.set_trace()
        start = self.ends[0]  # randomly choosing one end of the chain as start
        all_keys = list(all_ends.keys())
        while len(self.sorted) < len(self.bubbles):
            for idx, key in enumerate(all_keys):
                if start in key:
                    rm_key = idx
                    start = key[1 - key.index(start)]
                    self.sorted.append(all_ends[key])
                    break
            del all_keys[rm_key]

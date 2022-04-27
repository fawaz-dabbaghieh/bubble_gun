class Bubble:
    """
    Bubble object that has the important information about a bubble
    """
    __slots__ = ['source', 'sink', 'inside', 'key', 'id', 'parent_chain', 'parent_sb', 'chain_id']

    def __init__(self, source, sink, inside):
        """
        Initialize the bubble object
        """
        self.source = source
        self.sink = sink
        self.inside = inside
        self.key = self.__key()
        self.id = 0
        self.parent_chain = 0
        self.parent_sb = 0
        self.chain_id = 0
        # self.visited = False  # I need this when finding chains

    def __len__(self):
        """
        overloading the length function
        """
        return len(self.inside) + 2

    def __key(self):
        source = str(self.source.id)
        sink = str(self.sink.id)
        if source > sink:
            return (source, sink)
        return (sink, source)

    # I need to hash the bubbles because I can find the same bubble
    # twice as I'm coming from different directions
    # this way I can avoid adding it twice to the list of bubbles
    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return self.key == other.key

    def __ne__(self, other):
        return not self.__eq__(other)

    def list_bubble(self):
        """"
        returns a list of node ids that make up the bubble
        """
        node_list = [self.source.id, self.sink.id]
        for n in self.inside:
            node_list.append(n.id)
        return node_list

    def length_node(self):
        """
        returns how many nodes in the bubble including source and sink
        """
        return len(self.inside) + 2  # +2 for source and sink

    def length_seq(self):
        """
        returns the total sequence in the bubble
        """
        total_seq = self.source.seq_len + self.sink.seq_len
        for n in self.inside:
            total_seq += n.seq_len
        return total_seq

    def is_simple(self):
        """
        returns true if it's a simple bubble
        """
        if len(self.inside) == 2:
            return True
        return False

    def is_insertion(self):
        """
        returns true if it's an insertion
        i.e. bubble with one branch
        """
        if len(self.inside) == 1:
            return True
        return False

    def is_super(self):
        """
        returns true if it's a superbubble
        """
        if len(self.inside) > 2:
            return True
        return False

    def set_as_visited(self):
        """
        sets all the nodes of the bubble as visited
        """
        self.source.visited = True
        self.sink.visited = True
        for n in self.inside:
            n.visited = True

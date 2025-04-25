import logging
import sys
import pdb
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

    # def sort(self):
    #     """
    #     sorts the bubbles in the chain
    #
    #     Note: This function is an improvement on the last one and done by ScottMastro in Issue #8
    #     """
    #
    #     # Step 1: Build a mapping from each node ID to its connected bubbles
    #     node_to_bubbles = dict()
    #     for b in self.bubbles:
    #         for node_id in [str(b.source.id), str(b.sink.id)]:
    #             if node_id not in node_to_bubbles:
    #                 node_to_bubbles[node_id] = []
    #             node_to_bubbles[node_id].append(b)
    #
    #     # Step 2: Start at one end of the chain
    #     current_node = self.ends[0]
    #     visited_bubbles = set()
    #
    #     # Step 3: Traverse the chain using bubble adjacency
    #     while True:
    #         candidates = node_to_bubbles.get(current_node, [])
    #         next_bubble = None
    #
    #         for b in candidates:
    #             if b not in visited_bubbles:
    #                 next_bubble = b
    #                 break
    #
    #         if next_bubble is None:  # shouldn't happen in a valid chain
    #             logging.error("No unvisited bubble found: break in bubble chain. Stopping traversal.")
    #             sys.exit(1)
    #
    #         self.sorted.append(next_bubble)
    #         visited_bubbles.add(next_bubble)
    #
    #         # Step 4: Move to the next node
    #         if str(next_bubble.source.id) == current_node:
    #             current_node = str(next_bubble.sink.id)
    #         else:
    #             current_node = str(next_bubble.source.id)
    #         if len(self.sorted) == len(self.bubbles):
    #             break

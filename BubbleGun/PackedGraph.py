import os
import sys
from array import array


class PackedGraph:
    """
    Read-only graph representation with dense internal node indexing.

    Nodes are addressed internally by 0-based indices. Each oriented side is
    encoded as a handle: ``handle = (node_idx << 1) | side`` where ``side`` is
    ``0`` for start and ``1`` for end.
    """

    __slots__ = [
        "id_to_idx",
        "idx_to_id",
        "seq_lens",
        "sequences",
        "optional_info",
        "side_offsets",
        "adjacent_handles",
        "overlaps",
        "edge_count",
        "b_chains",
        "bubbles",
        "compacted",
        "node_visit_marks",
        "handle_seen_marks",
        "handle_stack_marks",
        "node_visit_epoch",
        "handle_seen_epoch",
        "handle_stack_epoch",
    ]

    def __init__(self, graph_file=None, store_sequences=True, store_optional_info=True):
        self.id_to_idx = {}
        self.idx_to_id = []
        self.seq_lens = array("I")
        self.sequences = [] if store_sequences else None
        self.optional_info = [] if store_optional_info else None
        self.side_offsets = array("I", [0])
        self.adjacent_handles = array("I")
        self.overlaps = array("I")
        self.edge_count = 0
        self.b_chains = set()
        self.bubbles = {}
        self.compacted = False
        self.node_visit_marks = array("I")
        self.handle_seen_marks = array("I")
        self.handle_stack_marks = array("I")
        self.node_visit_epoch = 0
        self.handle_seen_epoch = 0
        self.handle_stack_epoch = 0

        if graph_file is not None:
            if not os.path.exists(graph_file):
                print("graph file {} does not exist".format(graph_file))
                sys.exit()
            self._read_gfa(
                gfa_file_path=graph_file,
                store_sequences=store_sequences,
                store_optional_info=store_optional_info,
            )

    def __len__(self):
        return len(self.idx_to_id)

    @staticmethod
    def make_handle(node_idx, side):
        return (node_idx << 1) | side

    @staticmethod
    def handle_to_idx(handle):
        return handle >> 1

    @staticmethod
    def handle_to_side(handle):
        return handle & 1

    def get_idx(self, node_id):
        return self.id_to_idx[node_id]

    def get_id(self, node_idx):
        return self.idx_to_id[node_idx]

    def seq_len(self, node_idx):
        return self.seq_lens[node_idx]

    def sequence(self, node_idx):
        if self.sequences is None:
            return None
        return self.sequences[node_idx]

    def tags(self, node_idx):
        if self.optional_info is None:
            return None
        return self.optional_info[node_idx]

    def total_seq_length(self):
        return sum(self.seq_lens)

    def side_degree(self, node_idx, direction):
        start, end = self._side_range(node_idx, direction)
        return end - start

    def iter_edges(self, node_idx, direction):
        start, end = self._side_range(node_idx, direction)
        for offset in range(start, end):
            handle = self.adjacent_handles[offset]
            yield self.handle_to_idx(handle), self.handle_to_side(handle), self.overlaps[offset]

    def iter_children_handles(self, node_idx, direction):
        start, end = self._side_range(node_idx, direction)
        for offset in range(start, end):
            yield self.adjacent_handles[offset]

    def iter_children(self, node_idx, direction):
        for handle in self.iter_children_handles(node_idx, direction):
            yield self.handle_to_idx(handle)

    def children(self, node_idx, direction):
        return list(self.iter_children(node_idx, direction))

    def children_ids(self, node_id, direction):
        node_idx = self.get_idx(node_id)
        child_ids = [self.get_id(idx) for idx in self.iter_children(node_idx, direction)]
        return sorted(child_ids)

    def neighbors(self, node_idx):
        neighbor_indices = set(self.iter_children(node_idx, 0))
        neighbor_indices.update(self.iter_children(node_idx, 1))
        return sorted(neighbor_indices)

    def neighbor_pair(self, node_idx):
        first = []
        for direction in (0, 1):
            start, end = self._side_range(node_idx, direction)
            for offset in range(start, end):
                first.append(self.handle_to_idx(self.adjacent_handles[offset]))
        first.sort()
        return tuple(first)

    def has_neighbor(self, node_idx, other_idx):
        for direction in (0, 1):
            for neighbor_idx in self.iter_children(node_idx, direction):
                if neighbor_idx == other_idx:
                    return True
        return False

    def neighbors_ids(self, node_id):
        node_idx = self.get_idx(node_id)
        return sorted(self.get_id(idx) for idx in self.neighbors(node_idx))

    def add_chain(self, chain):
        if len(chain.sorted) == 0:
            chain.find_ends()
            if len(chain.ends) != 2:
                return
            chain.sort()
            if chain not in self.b_chains:
                self.b_chains.add(chain)

    def longest_chain_bubble(self):
        return max(self.b_chains, key=len)

    def longest_chain_seq(self):
        return max(self.b_chains, key=lambda chain: chain.length_seq(self))

    def nodes_in_chains(self):
        all_nodes = set()
        for chain in self.b_chains:
            all_nodes.update(chain.list_chain())
        return all_nodes

    def chain_cov_node(self):
        return float((len(self.nodes_in_chains()) * 100) / len(self))

    def chain_cov_seq(self):
        chains_nodes = self.nodes_in_chains()
        total_seq = 0
        for node_idx in chains_nodes:
            total_seq += self.seq_lens[node_idx]
        return (total_seq * 100) / float(self.total_seq_length())

    def bubble_number(self):
        counter = [0, 0, 0]
        for chain in self.b_chains:
            for bubble in chain.bubbles:
                if bubble.is_simple():
                    counter[0] += 1
                elif bubble.is_super():
                    counter[1] += 1
                elif bubble.is_insertion():
                    counter[2] += 1
        return counter

    def next_search_epochs(self):
        self.node_visit_epoch += 1
        self.handle_seen_epoch += 1
        self.handle_stack_epoch += 1
        return self.node_visit_epoch, self.handle_seen_epoch, self.handle_stack_epoch

    def _side_range(self, node_idx, direction):
        handle = self.make_handle(node_idx, direction)
        return self.side_offsets[handle], self.side_offsets[handle + 1]

    def _read_gfa(self, gfa_file_path, store_sequences, store_optional_info):
        with open(gfa_file_path, "r") as lines:
            for raw_line in lines:
                if not raw_line.startswith("S"):
                    continue

                line = raw_line.rstrip("\n").split("\t")
                node_id = line[1]
                if node_id in self.id_to_idx:
                    raise ValueError("Duplicate node id {} in {}".format(node_id, gfa_file_path))

                node_idx = len(self.idx_to_id)
                self.id_to_idx[node_id] = node_idx
                self.idx_to_id.append(node_id)

                sequence = line[2]
                self.seq_lens.append(len(sequence))
                if store_sequences:
                    self.sequences.append(sequence)
                if store_optional_info:
                    self.optional_info.append("\t".join(line[3:]) if len(line) > 3 else "")

        side_counts = array("I", [0]) * (2 * len(self.idx_to_id))
        self.edge_count = self._count_adjacencies(gfa_file_path, side_counts)

        self.side_offsets = array("I", [0]) * (len(side_counts) + 1)
        running_total = 0
        for index, count in enumerate(side_counts):
            self.side_offsets[index] = running_total
            running_total += count
        self.side_offsets[len(side_counts)] = running_total

        self.adjacent_handles = array("I", [0]) * running_total
        self.overlaps = array("I", [0]) * running_total
        cursor = array("I", self.side_offsets[:-1])
        self._fill_adjacencies(gfa_file_path, cursor)
        self.node_visit_marks = array("I", [0]) * len(self.idx_to_id)
        self.handle_seen_marks = array("I", [0]) * len(side_counts)
        self.handle_stack_marks = array("I", [0]) * len(side_counts)

    def _count_adjacencies(self, gfa_file_path, side_counts):
        edge_count = 0
        with open(gfa_file_path, "r") as lines:
            for raw_line in lines:
                if not raw_line.startswith("L"):
                    continue

                source_handle, target_handle, _ = self._parse_link(raw_line)
                side_counts[source_handle] += 1
                side_counts[target_handle] += 1
                edge_count += 1
        return edge_count

    def _fill_adjacencies(self, gfa_file_path, cursor):
        with open(gfa_file_path, "r") as lines:
            for raw_line in lines:
                if not raw_line.startswith("L"):
                    continue

                source_handle, target_handle, overlap = self._parse_link(raw_line)

                position = cursor[source_handle]
                self.adjacent_handles[position] = target_handle
                self.overlaps[position] = overlap
                cursor[source_handle] += 1

                reverse_position = cursor[target_handle]
                self.adjacent_handles[reverse_position] = source_handle
                self.overlaps[reverse_position] = overlap
                cursor[target_handle] += 1

    def _parse_link(self, raw_line):
        line = raw_line.split()

        first_node = line[1]
        second_node = line[3]
        if first_node not in self.id_to_idx:
            raise ValueError(
                "an edge between {} and {} exists but {} is missing".format(
                    first_node, second_node, first_node
                )
            )
        if second_node not in self.id_to_idx:
            raise ValueError(
                "an edge between {} and {} exists but {} is missing".format(
                    first_node, second_node, second_node
                )
            )

        source_side = 0 if line[2] == "-" else 1
        target_side = 1 if line[4] == "-" else 0
        if line[5] == "*":
            overlap = 0
        else:
            overlap = int(line[5][:-1])

        source_handle = self.make_handle(self.id_to_idx[first_node], source_side)
        target_handle = self.make_handle(self.id_to_idx[second_node], target_side)
        return source_handle, target_handle, overlap

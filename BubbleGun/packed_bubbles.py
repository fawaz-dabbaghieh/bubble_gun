import logging
import sys
from collections import Counter


class PackedBubble:
    __slots__ = ["source", "sink", "inside", "key", "id", "parent_chain", "parent_sb", "chain_id", "bubble_type"]

    def __init__(self, graph, source, sink, inside):
        self.source = source
        self.sink = sink
        self.inside = inside
        self.key = self.__key()
        self.id = 0
        self.parent_chain = 0
        self.parent_sb = 0
        self.chain_id = 0
        self.bubble_type = self._classify(graph)

    def __len__(self):
        return len(self.inside) + 2

    def __key(self):
        if self.source > self.sink:
            return (self.source, self.sink)
        return (self.sink, self.source)

    def __hash__(self):
        return hash(self.key)

    def __eq__(self, other):
        return self.key == other.key

    def list_bubble(self):
        return [self.source, self.sink] + list(self.inside)

    def length_seq(self, graph):
        total_seq = graph.seq_len(self.source) + graph.seq_len(self.sink)
        for node_idx in self.inside:
            total_seq += graph.seq_len(node_idx)
        return total_seq

    def _classify(self, graph):
        if len(self.inside) == 2:
            first = self.inside[0]
            second = self.inside[1]
            if (
                graph.side_degree(first, 0) == 1
                and graph.side_degree(first, 1) == 1
                and graph.side_degree(second, 0) == 1
                and graph.side_degree(second, 1) == 1
                and graph.neighbor_pair(first) == graph.neighbor_pair(second)
                and not graph.has_neighbor(self.source, self.sink)
            ):
                return "simple"

        if len(self.inside) == 1:
            middle = self.inside[0]
            if (
                graph.side_degree(middle, 0) == 1
                and graph.side_degree(middle, 1) == 1
                and tuple(sorted((self.source, self.sink))) == graph.neighbor_pair(middle)
            ):
                return "insertion"

        return "super"

    def is_simple(self):
        return self.bubble_type == "simple"

    def is_insertion(self):
        return self.bubble_type == "insertion"

    def is_super(self):
        return self.bubble_type == "super"


class PackedBubbleChain:
    __slots__ = ["bubbles", "sorted", "ends", "id", "parent_chain", "parent_sb"]

    def __init__(self):
        self.bubbles = set()
        self.sorted = []
        self.ends = []
        self.id = 0
        self.parent_chain = 0
        self.parent_sb = 0

    def __key(self):
        if self.ends[0] > self.ends[1]:
            return self.ends[0], self.ends[1]
        return self.ends[1], self.ends[0]

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return self.__key() == other.__key()

    def __len__(self):
        return len(self.bubbles)

    def add_bubble(self, bubble):
        self.bubbles.add(bubble)

    def list_chain(self):
        chain_nodes = set()
        for bubble in self.bubbles:
            chain_nodes.add(bubble.source)
            chain_nodes.add(bubble.sink)
            chain_nodes.update(bubble.inside)
        return list(chain_nodes)

    def length_seq(self, graph):
        total_seq = 0
        for node_idx in self.list_chain():
            total_seq += graph.seq_len(node_idx)
        return total_seq

    def find_ends(self):
        endpoints = [bubble.source for bubble in self.bubbles] + [bubble.sink for bubble in self.bubbles]
        self.ends = [node_idx for node_idx, count in Counter(endpoints).items() if count == 1]

    def sort(self):
        node_to_bubbles = {}
        for bubble in self.bubbles:
            node_to_bubbles.setdefault(bubble.source, set()).add(bubble)
            node_to_bubbles.setdefault(bubble.sink, set()).add(bubble)

        current_node = self.ends[0]
        visited_bubbles = set()
        while len(self.sorted) < len(self.bubbles):
            candidates = node_to_bubbles.get(current_node, set())
            next_bubble = None
            for bubble in candidates:
                if bubble not in visited_bubbles:
                    next_bubble = bubble
                    break

            if next_bubble is None:
                logging.error("No unvisited bubble found: break in bubble chain. Stopping traversal.")
                break

            self.sorted.append(next_bubble)
            visited_bubbles.add(next_bubble)
            if next_bubble.source == current_node:
                current_node = next_bubble.sink
            else:
                current_node = next_bubble.source


def _find_bubble_data_packed(graph, source_idx, direction):
    side_offsets = graph.side_offsets
    adjacent_handles = graph.adjacent_handles
    source_handle = (source_idx << 1) | direction
    seen_handles = {source_handle}
    visited = set()
    nodes_inside = []
    stack = [source_handle]
    stack_members = {source_handle}

    while stack:
        handle = stack.pop()
        stack_members.remove(handle)
        node_idx = handle >> 1
        node_direction = handle & 1
        visited.add(node_idx)
        nodes_inside.append(node_idx)
        seen_handles.discard(handle)

        start = side_offsets[handle]
        end = side_offsets[handle + 1]
        if start == end:
            break

        for offset in range(start, end):
            target_handle = adjacent_handles[offset]
            child_idx = target_handle >> 1
            child_side = target_handle & 1
            child_direction = 1 - child_side
            if child_idx == source_idx:
                stack.clear()
                stack_members.clear()
                break

            child_handle = (child_idx << 1) | child_direction
            seen_handles.add(child_handle)

            parent_handle = (child_idx << 1) | child_side
            parent_start = side_offsets[parent_handle]
            parent_end = side_offsets[parent_handle + 1]
            all_parents_visited = True
            for parent_offset in range(parent_start, parent_end):
                parent_idx = adjacent_handles[parent_offset] >> 1
                if parent_idx not in visited:
                    all_parents_visited = False
                    break

            if all_parents_visited and child_handle not in stack_members:
                stack.append(child_handle)
                stack_members.add(child_handle)

        if (len(stack_members) == 1) and (len(seen_handles) == 1):
            sink_handle = next(iter(stack_members))
            sink_idx = sink_handle >> 1
            nodes_inside.append(sink_idx)
            if len(nodes_inside) == 2:
                break

            return sink_idx, nodes_inside[1:-1]

    return None


def find_sb_alg_packed(graph, source_idx, direction, only_simple=False, only_super=False):
    bubble_data = _find_bubble_data_packed(graph, source_idx, direction)
    if bubble_data is None:
        return None

    sink_idx, inside = bubble_data
    bubble = PackedBubble(graph, source=source_idx, sink=sink_idx, inside=inside)

    if only_simple:
        if bubble.is_simple():
            return bubble
    elif only_super:
        if bubble.is_super():
            return bubble
    else:
        return bubble

    return None


def find_bubbles_packed(graph, only_simple=False, only_super=False):
    if only_simple and only_super:
        print("You can't mix both only_super and only_simple, choose one or not add these arguments to detect both")
        sys.exit(1)

    graph.bubbles = {}
    for node_idx in range(len(graph)):
        for direction in (0, 1):
            bubble = find_sb_alg_packed(graph, node_idx, direction, only_simple, only_super)
            if bubble is not None:
                graph.bubbles[bubble.key] = bubble


def connect_bubbles_packed(graph):
    ids_to_bubbles = {}
    for bubble in graph.bubbles.values():
        ids_to_bubbles.setdefault(bubble.source, set()).add(bubble)
        ids_to_bubbles.setdefault(bubble.sink, set()).add(bubble)

    starting_nodes = [node_idx for node_idx, bubbles in ids_to_bubbles.items() if len(bubbles) == 1]
    logging.info("Got the %s starting nodes of bubbles to construct chains...", len(starting_nodes))

    def build_chain(start_node):
        chain = PackedBubbleChain()
        current_node = start_node
        while True:
            bubbles_at_node = ids_to_bubbles.get(current_node)
            if not bubbles_at_node:
                break
            current_bubble = bubbles_at_node.pop()
            chain.add_bubble(current_bubble)
            if current_node == current_bubble.source:
                next_node = current_bubble.sink
            else:
                next_node = current_bubble.source
            next_set = ids_to_bubbles.get(next_node)
            if next_set is not None:
                next_set.discard(current_bubble)
            current_node = next_node
        return chain

    graph.b_chains = set()
    for node_idx in starting_nodes:
        if not ids_to_bubbles.get(node_idx):
            continue
        chain = build_chain(node_idx)
        if len(chain) != 0:
            chain.find_ends()
            graph.add_chain(chain)

    for node_idx, bubbles in ids_to_bubbles.items():
        if not bubbles:
            continue
        chain = build_chain(node_idx)
        if len(chain) != 0:
            chain.find_ends()
            graph.add_chain(chain)

    bubble_counter = 1
    chain_counter = 1
    for chain in graph.b_chains:
        chain.id = chain_counter
        for bubble in chain.sorted:
            bubble.id = bubble_counter
            bubble.chain_id = chain.id
            bubble_counter += 1
        chain_counter += 1


def find_parents_packed(graph):
    all_sbs = [bubble for bubble in graph.bubbles.values() if bubble.is_super()]
    all_sbs = sorted(all_sbs, key=lambda bubble: len(bubble.inside), reverse=True)

    for sb in all_sbs:
        for node_idx in sb.inside:
            for direction in (0, 1):
                bubble_data = _find_bubble_data_packed(graph, node_idx, direction)
                if bubble_data is None:
                    continue
                sink_idx, _ = bubble_data
                bubble_key = (sink_idx, node_idx) if sink_idx > node_idx else (node_idx, sink_idx)
                if bubble_key in graph.bubbles:
                    graph.bubbles[bubble_key].parent_sb = sb.id
                    graph.bubbles[bubble_key].parent_chain = sb.chain_id

    for chain in graph.b_chains:
        for bubble in chain.bubbles:
            if bubble.parent_sb != 0:
                chain.parent_sb = bubble.parent_sb
                chain.parent_chain = bubble.parent_chain
                break

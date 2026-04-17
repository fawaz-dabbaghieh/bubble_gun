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
            first_start = graph.unique_side_neighbors(first, 0)
            first_end = graph.unique_side_neighbors(first, 1)
            second_start = graph.unique_side_neighbors(second, 0)
            second_end = graph.unique_side_neighbors(second, 1)
            if (
                len(first_start) == 1
                and len(first_end) == 1
                and len(second_start) == 1
                and len(second_end) == 1
                and graph.neighbor_pair(first) == graph.neighbor_pair(second)
                and not graph.has_neighbor(self.source, self.sink)
            ):
                return "simple"

        if len(self.inside) == 1:
            middle = self.inside[0]
            middle_start = graph.unique_side_neighbors(middle, 0)
            middle_end = graph.unique_side_neighbors(middle, 1)
            if (
                len(middle_start) == 1
                and len(middle_end) == 1
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
    node_visit_marks = graph.node_visit_marks
    handle_seen_marks = graph.handle_seen_marks
    handle_stack_marks = graph.handle_stack_marks
    visit_epoch, seen_epoch, stack_epoch = graph.next_search_epochs()
    source_handle = (source_idx << 1) | direction
    nodes_inside = []
    stack = [source_handle]
    stack_count = 1
    seen_count = 1
    handle_seen_marks[source_handle] = seen_epoch
    handle_stack_marks[source_handle] = stack_epoch

    while stack:
        handle = stack.pop()
        handle_stack_marks[handle] = 0
        stack_count -= 1
        node_idx = handle >> 1
        node_direction = handle & 1
        node_visit_marks[node_idx] = visit_epoch
        nodes_inside.append(node_idx)
        if handle_seen_marks[handle] == seen_epoch:
            handle_seen_marks[handle] = 0
            seen_count -= 1

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
                stack_count = 0
                break

            child_handle = (child_idx << 1) | child_direction
            if handle_seen_marks[child_handle] != seen_epoch:
                handle_seen_marks[child_handle] = seen_epoch
                seen_count += 1

            parent_handle = (child_idx << 1) | child_side
            parent_start = side_offsets[parent_handle]
            parent_end = side_offsets[parent_handle + 1]
            all_parents_visited = True
            for parent_offset in range(parent_start, parent_end):
                parent_idx = adjacent_handles[parent_offset] >> 1
                if node_visit_marks[parent_idx] != visit_epoch:
                    all_parents_visited = False
                    break

            if all_parents_visited and handle_stack_marks[child_handle] != stack_epoch:
                stack.append(child_handle)
                handle_stack_marks[child_handle] = stack_epoch
                stack_count += 1

        if (stack_count == 1) and (seen_count == 1):
            sink_handle = stack[-1]
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
    node_to_superbubbles = {}
    for sb in all_sbs:
        for node_idx in sb.inside:
            node_to_superbubbles.setdefault(node_idx, []).append(sb)

    for bubble in graph.bubbles.values():
        bubble_nodes = list(dict.fromkeys(bubble.list_bubble()))
        if not bubble_nodes:
            continue

        candidate_counts = {}
        for node_idx in bubble_nodes:
            for sb in node_to_superbubbles.get(node_idx, ()):
                candidate_counts[sb] = candidate_counts.get(sb, 0) + 1

        parent_candidates = [
            sb
            for sb, count in candidate_counts.items()
            if count == len(bubble_nodes) and sb.key != bubble.key
        ]

        if parent_candidates:
            parent_sb = min(parent_candidates, key=lambda sb: (len(sb.inside), sb.id))
            bubble.parent_sb = parent_sb.id
            bubble.parent_chain = parent_sb.chain_id

    for chain in graph.b_chains:
        for bubble in chain.bubbles:
            if bubble.parent_sb != 0:
                chain.parent_sb = bubble.parent_sb
                chain.parent_chain = bubble.parent_chain
                break

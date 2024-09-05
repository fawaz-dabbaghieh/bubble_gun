from time import time
from datetime import datetime


def current_time():
    return datetime.fromtimestamp(time()).strftime('%Y-%m-%d %H:%M:%S')


def reverse_complement(dna):
    complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A', 'N':'N', "*":"*"}
    return ''.join([complement[base] for base in dna[::-1]])


def calculate_n50(graph):
    list_of_lengths = []
    for n in graph.nodes.values():
        list_of_lengths.append(n.seq_len)
    list_of_lengths = sorted(list_of_lengths)
    new_list = []
    for x in list_of_lengths:
        new_list += [x]*x
    if len(new_list) % 2 == 0:
        medianpos = int(len(new_list)/2)
        return float(new_list[medianpos] + new_list[medianpos-1])/2
    else:
        medianpos = int(len(new_list)/2)
        return new_list[medianpos]


def bfs(graph, start_node, size):
    """
    Returns a neighborhood of size given around start node

    :param graph: A graph object from class Graph
    :param start_node: starting node for the BFS search
    :param size: size of the neighborhood to return
    """

    queue = []
    neighborhood = set()
    visited = set()

    queue.append(start_node)
    visited.add(start_node)
    neighborhood.add(start_node)

    neighbors = graph.nodes[start_node].neighbors()

    if len(neighbors) == 0:  # start node was a lonely node
        return neighborhood

    # break when the subgraph is longer than the size wanted
    # or the component the start node in was smaller than the size
    while (len(neighborhood) <= size) and len(queue) > 0:
        start = queue.pop()

        if start not in neighborhood:
            neighborhood.add(start)

        visited.add(start)
        neighbors = graph.nodes[start].neighbors()
        for n in neighbors:
            if n not in visited:
                queue.append(n)

    return neighborhood
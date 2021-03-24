from BubbleGun.functions import reverse_complement


def next_direction(node1, node2, direction):
    """
    returns the next direction to look for a neighbor

    :param node1: node object
    :param node2: another node object
    :return: 0 or 1 for next direction
    """
    if direction == 0:
        for n in node1.start:
            if node2.id == n[0]:
                return 1 - n[1], n[2]  # flipping 0 and 1

    elif direction == 1:
        for n in node1.end:
            if node2.id == n[0]:
                return 1 - n[1], n[2]  # flipping 0 and 1


def path_checker(graph, path):
    """
    checks if there's an actual path connecting the ordered nodes in path

    :param path: list of node ids, ordered according to the path
    :param graph: Graph object
    :return: Boolean
    """

    if len(path) <= 1:
        return False

    # I don't know where to look first
    if graph.nodes[path[0]].in_direction(path[1], 0):
        direction = 0
    elif graph.nodes[path[0]].in_direction(path[1], 1):
        direction = 1
    else:
        # first two nodes are not connected
        return False

    # todo somewhere here is wrong
    for i in range(len(path) - 1):
        current_node = graph.nodes[path[i]]
        next_node = graph.nodes[path[i+1]]

        if current_node.in_direction(next_node.id, direction):
            direction, overlap = next_direction(current_node, next_node, direction)
        else:
            return False

    return True


def sequence_extractor(graph, path):
    """
    returns the sequence of the path

    :param graph: a graph object
    :param path: a list of nodes ordered according to the path
    :return: sequence of the path
    """

    # check if path exists
    if len(path) == 1:
        return graph.nodes[path[0]].seq

    elif not path_checker(graph, path):
        return ""

    if graph.nodes[path[0]].in_direction(graph.nodes[path[1]].id, 0):
        direction = 0
        sequence = reverse_complement(graph.nodes[path[0]].seq)
    elif graph.nodes[path[0]].in_direction(graph.nodes[path[1]].id, 1):
        direction = 1
        sequence = graph.nodes[path[0]].seq

    for i in range(len(path) - 1):
        current_node = graph.nodes[path[i]]
        next_node = graph.nodes[path[i+1]]
        if current_node.in_direction(next_node.id, direction):
            direction, overlap = next_direction(current_node, next_node, direction)
            # if next direction is one this means current node connects to
            # next node from 0 so I don't need to take the reverse complement
            # Otherwise I need to
            if direction == 1:
                sequence += next_node.seq[overlap:]
            else:
                sequence += reverse_complement(next_node.seq)[overlap:]

    return sequence

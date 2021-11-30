from collections import deque


def main_while_loop(graph, start_node, queue, direction, visited, size):
    neighborhood = {start_node}
    if len(queue) == 0:
        queue.append(start_node)

    while (len(neighborhood) <= size) and len(queue) > 0:
        start = queue.popleft()

        if start not in neighborhood:
            neighborhood.add(start)

        visited.add(start)

        if start == start_node:
            neighbors = graph.nodes[start_node].children(direction)
        else:
            neighbors = graph.nodes[start].neighbors()

        for n in neighbors:
            if n not in visited:
                queue.append(n)

    return neighborhood


def bfs(graph, start_node, size):
    """
    Runs bfs and returns the neighborhood smaller than size

    Using only bfs was resulting in a one-sided neighborhood.
    So the neighborhood I was getting was mainly going from the start node
    into one direction because we have FIFO and it basically keeps going
    in that direction. So I decided to split check if have two possible directions
    From start, too look in both directions separately and add that to the whole neighborhood

    :param graph: A graph object from class Graph
    :param start_node: starting node for the BFS search
    :param size: size of the neighborhood to return
    """

    queue = deque()
    visited = set()

    # I will in both direction, and search for half the neighborhood in one
    # and the other half in the other direction
    # if the nieghborhood is 100, I will traverse 50 to the right and 50 to the left and return that
    queue.append(start_node)
    visited.add(start_node)
    first_direction = graph.nodes[start_node].children(0)
    len_first_direction = 0
    second_direction = graph.nodes[start_node].children(1)
    len_second_direction = 0
    # neighbors = graph.nodes[start_node].neighbors()

    if len(first_direction) == 0:
        if len(second_direction) == 0:
            return {start_node}
        else:
            len_second_direction = size
    else:
        if len(second_direction) == 0:
            len_first_direction = size
        else:
            len_first_direction = int(size/2)
            len_second_direction = int(size/2)

    # if len(neighbors) == 0:  # start node was a lonely node
    #     return neighborhood

    # break when the subgraph is longer than the size wanted
    # or the component the start node in was smaller than the size
    neighborhood = main_while_loop(graph, start_node, queue, 0, visited, len_first_direction)

    queue = deque()
    if len(neighborhood) < int(size/2):
        len_second_direction += size - int(size/2)

    neighborhood = neighborhood.union(main_while_loop(graph, start_node, queue, 1, visited, len_second_direction))

    # while (len(neighborhood) <= len_first_direction) and len(queue) > 0:
    #     start = queue.popleft()
    #
    #     if start not in neighborhood:
    #         neighborhood.add(start)
    #
    #     visited.add(start)
    #
    #     if start == start_node:
    #         neighbors = first_direction
    #     else:
    #         neighbors = graph.nodes[start].neighbors()
    #
    #     for n in neighbors:
    #         if n not in visited:
    #             queue.append(n)
    #
    # queue = deque()
    # queue.append(start_node)
    # # in case on direction had only a few nodes then
    # # then I explore more than half of the size in the other direction
    # if len(neighborhood) < int(size/2):
    #     len_second_direction += size - int(size/2)
    #
    # while (len(neighborhood) <= len_second_direction) and len(queue) > 0:
    #     start = queue.popleft()
    #
    #     if start not in neighborhood:
    #         neighborhood.add(start)
    #
    #     visited.add(start)
    #
    #     if start == start_node:
    #         neighbors = first_direction
    #     else:
    #         neighbors = graph.nodes[start].neighbors()
    #
    #     for n in neighbors:
    #         if n not in visited:
    #             queue.append(n)

    return neighborhood

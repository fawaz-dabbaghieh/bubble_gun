from collections import deque


def bfs(graph, start_node, size):
    """
    Runs bfs and returns the neighborhood smaller than size

    :param graph: A graph object from class Graph
    :param start_node: starting node for the BFS search
    :param size: size of the neighborhood to return
    """

    queue = deque()
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
        start = queue.popleft()

        if start not in neighborhood:
            neighborhood.add(start)

        visited.add(start)
        neighbors = graph.nodes[start].neighbors()
        for n in neighbors:
            if n not in visited:
                queue.append(n)

    return neighborhood
def find_component(graph, start_node):
    """
    Find component in the graph starting from given node

    :param graph: is a graph object from class Graph
    :param start_node: The start node of BFS search.
    :return: a list of node ids for the component
    """
    queue = []
    cc = set()

    # visited = set()
    queue.append(start_node)
    graph.nodes[start_node].visited = True
    # visited.add(start_node)
    neighbors = graph.nodes[start_node].neighbors()

    if len(neighbors) == 0:
        cc.add(start_node)
        return cc

    while len(queue) > 0:
        start = queue.pop()
        if start not in cc:
            cc.add(start)
        else:
            continue

        # visited.add(start)
        graph.nodes[start].visited = True
        neighbors = graph.nodes[start].neighbors()
        for n in neighbors:
            if not graph.nodes[n].visited:
                queue.append(n)

    return cc


def all_components(graph):
    """
    find all connected components in the graph

    :params graph: is a graph object from class Graph
    :return: list of list of components
    """

    graph.reset_visited()  # turns all nodes to False
    connected_comp = []
    # visited = set()
    for n in graph.nodes:
        # if n not in visited:
        if not graph.nodes[n].visited:
            connected_comp.append(find_component(graph, n))
            # visited = visited.union(connected_comp[-1])
    return connected_comp

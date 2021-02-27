from .functions import reverse_complement

"""
Compact a graph

recursive function for merging, I check one of the ends
and merge accordingly then call it again to check
if further merges can be done to that end
then I check the other end and do the same
merge_end check for merges from the "end" side of the node
or according to my structure it's given the number 1
merge_start checks for merges from the "start" side of the node,
or the "0" side
"""


def merge_end(graph, n):

    # print("in merge END with n {} and neighbor {}".format(n, nodes[n].end[0]))
    # print("and n's START are {}".format(nodes[n].start))
    nodes = graph.nodes
    k = graph.k

    if n != nodes[n].end[0][0]:  # no self loops
        neighbor = nodes[n].end[0]  # tuple (n_id, direction, overlap)
        # checking if the neighbor is connected at start (so we have + + edge)
        # and that it only have one node from the start which is n
        if (neighbor[1] == 0) and (len(nodes[neighbor[0]].start) == 1):
            # the ends of n becomes the ends of neighbor
            # I am copying the connections of neighbors on the opposite side
            # and removing neighbor node
            nodes[n].end += [(x[0], x[1]) for x in nodes[neighbor[0]].end]
            # the sequence and seq_len gets updated
            nodes[n].seq += nodes[neighbor[0]].seq[neighbor[2]:]
            nodes[n].seq_len = len(nodes[n].seq)
            # nodes[neighbor[0]] = None
            graph.remove_node(neighbor[0])
            # nodes[n].end = copy.deepcopy(nodes[neighbor[0]].end)
            # I think I can remove the neighbor node here with
            # Here I need to check the new neighbors at end, 
            # and remove the merged node
            # and add n to them
            for nn in nodes[n].end:
                overlap = nn[2]
                # We are connected to it from start
                if nn[1] == 0:
                    #nodes[nn[0]].start.remove((neighbor[0], 1))
                    nodes[nn[0]].start.append((n, 1, overlap))
                elif nn[1] == 1:
                    # the if else here needed in case of there was a self 
                    # loop on the end side of neighbor
                    # the self loops is added to the merged node
                    if nn[0] != neighbor[0]:
                        # nodes[nn[0]].end.remove((neighbor[0], 1))
                        nodes[nn[0]].end.append((n, 1, overlap))
                    else:
                        # nodes[n].end.remove((neighbor[0], 1))
                        nodes[n].end.append((n, 1, overlap))

            if len(nodes[n].end) == 1:
                merge_end(graph, n)

        elif (neighbor[1] == 1) and (len(nodes[neighbor[0]].end) == 1):
            # the ends of n becomes the start of neighbor (because it's flipped)
            # and the sequence and seq_len get updated
            # nodes[n].end = copy.deepcopy(nodes[neighbor[0]].start)
            # I think I can remove the neighbor node here with
            nodes[n].end += [(x[0], x[1]) for x in nodes[neighbor[0]].start]
            reverse = reverse_complement(nodes[neighbor[0]].seq)
            nodes[n].seq += reverse[neighbor[2]:]
            # nodes[n].seq += reverse[k - 1:]
            nodes[n].seq_len = len(nodes[n].seq)
            # nodes[neighbor[0]] = None

            graph.remove_node(neighbor[0])
            # Here I need to check the new neighbors at end of n, 
            # and remove the merged node
            # and add n to them
            for nn in nodes[n].end:
                overlap = nn[2]
                # We are connected to it from start
                if nn[1] == 0:
                    # the if else here needed in case of there was a 
                    # self loop on the end side of neighbor
                    # the self loops is added to the merged node
                    if nn[0] != neighbor[0]:
                        # nodes[nn[0]].start.remove((neighbor[0], 0))
                        nodes[nn[0]].start.append((n, 1, overlap))
                    else:
                        # nodes[n].end.remove((neighbor[0], 0))
                        nodes[n].end.append((n, 1, overlap))

                elif nn[1] == 1:
                    # nodes[nn[0]].end.remove((neighbor[0], 0))
                    nodes[nn[0]].end.append((n, 1, overlap))

            if len(nodes[n].end) == 1:
                merge_end(graph, n)


def merge_start(graph, n):
    # print("in merge START with n {} and neighbor {}".format(n, nodes[n].start[0]))
    # print("and n's END are {}".format(nodes[n].end))

    nodes = graph.nodes
    k = graph.k
    if n != nodes[n].start[0][0]:  # no self loop
        neighbor = nodes[n].start[0]
        # checking if the neighbor is connected at start (so we have - + edge)
        # and that it only have one node from the start which is n
        if (neighbor[1] == 0) and (len(nodes[neighbor[0]].start) == 1):
            # the start of n becomes the ends of neighbor
            # and the sequence and seq_len get updated
            # nodes[n].start = copy.deepcopy(nodes[neighbor[0]].end)
            nodes[n].start += [(x[0], x[1]) for x in nodes[neighbor[0]].end]

            reverse = reverse_complement(nodes[neighbor[0]].seq)
            nodes[n].seq = reverse[:len(reverse) - neighbor[2]] + nodes[n].seq
            nodes[n].seq_len = len(nodes[n].seq)
            # nodes[neighbor[0]] = None
            graph.remove_node(neighbor[0])
            # Here I need to check the new neighbors at end, and remove the merged node
            # and n to them
            for nn in nodes[n].start:
                overlap = nn[2]
                # We are connected to it from start
                if nn[1] == 0:
                    #nodes[nn[0]].start.remove((neighbor[0], 1))
                    nodes[nn[0]].start.append((n, 0, overlap))

                elif nn[1] == 1:
                    if nn[0] != neighbor[0]:
                        #nodes[nn[0]].end.remove((neighbor[0], 1))
                        nodes[nn[0]].end.append((n, 0, overlap))
                    else:
                        #nodes[n].start.remove((neighbor[0], 1))
                        nodes[n].start.append((n, 0, overlap))

            if len(nodes[n].start) == 1:
                merge_start(graph, n)

        elif (neighbor[1] == 1) and (len(nodes[neighbor[0]].end) == 1):
            merge_end(graph, neighbor[0])


def compact_graph(graph):
    node_ids = list(graph.nodes.keys())
    for n in node_ids:
        if n in graph.nodes:

            # print("I am at nodes {}".format(n))
            if len(graph.nodes[n].end) == 1:
                merge_end(graph, n)
            if len(graph.nodes[n].start) == 1:
                merge_start(graph, n)

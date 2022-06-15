from BubbleGun.functions import reverse_complement
import pdb

"""
Compact a graph

It's an updated version of the old recursive way to do compactness
This one uses a while loop instead of nested functions
Nested functions took too much memory when there were many nodes to compact
This doesn't take any extra memory than what's already stored.
"""


def merge_end(graph, n):
    # print("in merge END with n {} and neighbor {}".format(n, graph.nodes[n].end[0]))
    # print("and n's START are {}".format(graph.nodes[n].start))
    nodes = graph.nodes
    # k = graph.k

    if n != nodes[n].end[0][0]:  # no self loops
        neighbor = nodes[n].end[0]
        # checking if the neighbor is connected at start (so we have + + edge)
        # and that it only have one node from the start which is n
        if (neighbor[1] == 0) and (len(nodes[neighbor[0]].start) == 1):
            # the ends of n becomes the ends of neighbor
            # I am copying the connections of neighbors on the opposite side
            # and removing neighbor node
            new_ends = [x for x in nodes[neighbor[0]].end]
            nodes[n].end += [x for x in nodes[neighbor[0]].end]
            # the sequence and seq_len gets updated
            nodes[n].seq += nodes[neighbor[0]].seq[neighbor[2]:]
            # nodes[n].seq += nodes[neighbor[0]].seq[k - 1:]
            # adding the coverages and taking the mean
            # nodes[n].coverage = (nodes[n].coverage + nodes[neighbor[0]].coverage)/2

            nodes[n].seq_len = len(nodes[n].seq)
            # nodes[neighbor[0]] = None
            # print(f"Removing node {neighbor[0]}")
            graph.remove_node(neighbor[0])
            # I think I can remove the neighbor node here with
            # Here I need to check the new neighbors at end, 
            # and remove the merged nod
            # and add n to them

            # I needed new_ends because I can't iterate and change
            # nodes[n].end at the same time
            for nn in new_ends:
                overlap = nn[2]
                if nn[1] == 0:
                    # nodes[nn[0]].start.remove((neighbor[0], 1))
                    nodes[nn[0]].start.append((n, 1, overlap))
                elif nn[1] == 1:
                    # the if else here needed in case of there was a self 
                    # loop on the end side of neighbor
                    # the self loops is added to the merged node
                    if nn[0] != neighbor[0]:
                        # nodes[nn[0]].end.remove((neighbor[0], 1))
                        nodes[nn[0]].end.append((n, 1, overlap))
                    else:
                        try:
                            nodes[n].end.remove((neighbor[0], 1, overlap))
                            nodes[n].end.append((n, 1, overlap))
                        except:
                            pdb.set_trace()

            # if I reached here then I successfully compacted a node
            return True
            # if len(nodes[n].end) == 1:
            #     merge_end(graph, n)

        elif (neighbor[1] == 1) and (len(nodes[neighbor[0]].end) == 1):
            # the ends of n becomes the start of neighbor (because it's flipped)
            # and the sequence and seq_len get updated
            # nodes[n].end = copy.deepcopy(nodes[neighbor[0]].start)
            # I think I can remove the neighbor node here with
            new_ends = [x for x in nodes[neighbor[0]].start]
            nodes[n].end += [x for x in nodes[neighbor[0]].start]

            reverse = reverse_complement(nodes[neighbor[0]].seq)
            nodes[n].seq += reverse[neighbor[2]:]
            # nodes[n].seq += reverse[k - 1:]
            # nodes[n].coverage = (nodes[n].coverage + nodes[neighbor[0]].coverage)/2
            nodes[n].seq_len = len(nodes[n].seq)
            # nodes[neighbor[0]] = None
            # if neighbor[0] == 3827:
            #     pdb.set_trace()
            graph.remove_node(neighbor[0])
            # Here I need to check the new neighbors at end of n, 
            # and remove the merged node
            # and add n to them
            for nn in new_ends:
                overlap = nn[2]
                if nn[1] == 0:
                    # the if else here needed in case of there was a 
                    # self loop on the end side of neighbor
                    # the self loops is added to the merged node
                    if nn[0] != neighbor[0]:
                        # nodes[nn[0]].start.remove((neighbor[0], 0))
                        nodes[nn[0]].start.append((n, 1, overlap))
                    else:
                        try:
                            nodes[n].end.remove((neighbor[0], 0, overlap))
                            nodes[n].end.append((n, 1, overlap))
                        except:
                            pdb.set_trace()

                elif nn[1] == 1:
                    # nodes[nn[0]].end.remove((neighbor[0], 0))
                    nodes[nn[0]].end.append((n, 1, overlap))

            return True
            # if len(nodes[n].end) == 1:
            #     merge_end(graph, n)
    # if I'm here that mean none of the True returns were reached
    return False


def merge_start(graph, n):
    # print("in merge START with n {} and neighbor {}".format(n, graph.nodes[n].start[0]))
    # print("and n's END are {}".format(graph.nodes[n].end))

    nodes = graph.nodes
    # k = graph.k
    if n != nodes[n].start[0][0]:  # no self loop
        neighbor = nodes[n].start[0]
        # checking if the neighbor is connected at start (so we have - + edge)
        # and that it only have one node from the start which is n
        if (neighbor[1] == 0) and (len(nodes[neighbor[0]].start) == 1):
            # the start of n becomes the ends of neighbor
            # and the sequence and seq_len get updated
            # nodes[n].start = copy.deepcopy(nodes[neighbor[0]].end)
            starts = [x for x in nodes[neighbor[0]].end]
            # print(f"adding these new starts to start")
            nodes[n].start += [x for x in nodes[neighbor[0]].end]

            reverse = reverse_complement(nodes[neighbor[0]].seq)
            # nodes[n].seq = nodes[neighbor[0]].seq[:nodes[neighbor[0]].seq_len - (k - 1)] + nodes[n].seq

            nodes[n].seq = reverse[:len(reverse) - neighbor[2]] + nodes[n].seq
            nodes[n].seq_len = len(nodes[n].seq)
            # nodes[neighbor[0]] = None
            # if neighbor[0] == 3827:
            #     pdb.set_trace()
            graph.remove_node(neighbor[0])
            # Here I need to check the new neighbors at end, and remove the merged node
            # and add n to them
            for nn in starts:
                overlap = nn[2]
                # We are connected to it from start
                if nn[1] == 0:
                    # nodes[nn[0]].start.remove((neighbor[0], 1))
                    nodes[nn[0]].start.append((n, 0, overlap))

                elif nn[1] == 1:
                    if nn[0] != neighbor[0]:
                        # nodes[nn[0]].end.remove((neighbor[0], 1))
                        nodes[nn[0]].end.append((n, 0, overlap))
                    else:
                        try:
                            nodes[n].start.remove((neighbor[0], 1, overlap))
                            nodes[n].start.append((n, 0, overlap))
                        except:
                            pdb.set_trace()

            return True
            # if len(nodes[n].start) == 1:
            #     merge_start(graph, n)

        elif (neighbor[1] == 1) and (len(nodes[neighbor[0]].end) == 1):
            # the start of n becomes the ends of neighbor
            # and the sequence and seq_len get updated
            # nodes[n].start = copy.deepcopy(nodes[neighbor[0]].end)
            starts = [x for x in nodes[neighbor[0]].start]
            nodes[n].start += [x for x in nodes[neighbor[0]].start]

            reverse = reverse_complement(nodes[neighbor[0]].seq)
            nodes[n].seq = reverse[:len(reverse) - neighbor[2]] + nodes[n].seq
            # nodes[n].seq = reverse[:len(reverse) - (k - 1)] + nodes[n].seq
            nodes[n].seq_len = len(nodes[n].seq)
            # nodes[neighbor[0]] = Non
            # if neighbor[0] == 3827:
            #     pdb.set_trace()
            graph.remove_node(neighbor[0])
            # Here I need to check the new neighbors at end, and remove the merged node
            # and n to them
            for nn in starts:
                overlap = nn[2]
                # We are connected to new neighbor from start
                if nn[1] == 0:
                    if nn[0] != neighbor[0]:
                        nodes[nn[0]].start.append((n, 0, overlap))
                    else:
                        try:
                            nodes[n].start.remove((neighbor[0], 0, overlap))
                            nodes[n].start.append((n, 0, overlap))
                        except:
                            pdb.set_trace()
                elif nn[1] == 1:
                    nodes[nn[0]].end.append((n, 0, overlap))
            return True
    return False


def compact_graph(graph):
    # need to have a list of nodes to iterate through
    # can't iterate and change the same dictionary
    list_of_nodes = list(graph.nodes.keys())
    for n in list_of_nodes:
        if n in graph.nodes:
            # print("at node {}".format(n))
            # print("begin at node {}".format(n))
            # # checking it's not a node that already got merged in the while loop
            #     if graph.nodes[n] is not None:
            #         # checking if it has one neighbor and it's not a self loop
            # print("I am at node {}".format(n))
            while True:
                # pdb.set_trace()
                if len(graph.nodes[n].end) == 1:
                    # print("first while at node {}".format(n))
                    if not merge_end(graph, n):
                        break
                else:
                    break

            while True:
                # pdb.set_trace()
                # print("second while at node {}".format(n))
                if len(graph.nodes[n].start) == 1:
                    # print("at node {}".format(n))
                    if not merge_start(graph, n):
                        break
                else:
                    break

import sys
import os
import copy
from .functions import reverse_complement

# recursive function for merging, I check one of the ends, and merge accordingly then call it again to check
# if further merges can be done to that end, then I check the other end and do the same
# merge_end check for merges from the "end" side of the node, or according to my structure it's given the number 1
# merge_start checks for merges from the "start" side of the node, or the "0" side

def merge_end(nodes, n, k, none_nodes):
    # print("in merge END with n {} and neighbor {}".format(n, nodes[n].end[0]))
    # print("and n's START are {}".format(nodes[n].start))

    if n != nodes[n].end[0][0]:
        neighbor = nodes[n].end[0]
        # checking if the neighbor is connected at start (so we have + + edge)
        # and that it only have one node from the start which is n
        if (neighbor[1] == 0) and (len(nodes[neighbor[0]].start) == 1):
            # the ends of n becomes the ends of neighbor
            # and the sequence and seq_len gets updated
            nodes[n].end = copy.deepcopy(nodes[neighbor[0]].end)
            # Here I need to check the new neighbors at end, 
            # and remove the merged node
            # and n to them

            for nn in nodes[neighbor[0]].end:
                # We are connected to it from start
                if nn[1] == 0:

                    nodes[nn[0]].start.remove((neighbor[0], 1))
                    nodes[nn[0]].start.append((n, 1))

                elif nn[1] == 1:
                    # the if else here needed in case of there was a self 
                    # loop on the end side of neighbor
                    # the self loops is added to the merged node
                    if nn[0] != neighbor[0]:
                        nodes[nn[0]].end.remove((neighbor[0], 1))
                        nodes[nn[0]].end.append((n, 1))
                    else:
                        nodes[n].end.remove((neighbor[0], 1))
                        nodes[n].end.append((n, 1))

            nodes[n].seq += nodes[neighbor[0]].seq[k - 1:]
            nodes[n].seq_len = len(nodes[n].seq)
            nodes[neighbor[0]] = None
            none_nodes.append(neighbor[0])

            if len(nodes[n].end) == 1:
                merge_end(nodes, n, k, none_nodes)

        elif (neighbor[1] == 1) and (len(nodes[neighbor[0]].end) == 1):
            # the ends of n becomes the start of neighbor (because it's flipped)
            # and the sequence and seq_len get updated
            nodes[n].end = copy.deepcopy(nodes[neighbor[0]].start)
            # Here I need to check the new neighbors at end of n, 
            # and remove the merged node
            # and add n to them
            for nn in nodes[neighbor[0]].start:
                # We are connected to it from start
                if nn[1] == 0:
                    # the if else here needed in case of there was a 
                    # self loop on the end side of neighbor
                    # the self loops is added to the merged node
                    if nn[0] != neighbor[0]:
                        nodes[nn[0]].start.remove((neighbor[0], 0))
                        nodes[nn[0]].start.append((nodes[n].id, 1))
                    else:
                        nodes[n].end.remove((neighbor[0], 0))
                        nodes[n].end.append((n, 1))

                elif nn[1] == 1:
                    nodes[nn[0]].end.remove((neighbor[0], 0))
                    nodes[nn[0]].end.append((nodes[n].id, 1))

            reverse = reverse_complement(nodes[neighbor[0]].seq)

            nodes[n].seq += reverse[k - 1:]
            nodes[n].seq_len = len(nodes[n].seq)
            nodes[neighbor[0]] = None
            none_nodes.append(neighbor[0])

            if len(nodes[n].end) == 1:
                merge_end(nodes, n, k, none_nodes)

def merge_start(nodes, n, k, none_nodes):
    # print("in merge START with n {} and neighbor {}".format(n, nodes[n].start[0]))
    # print("and n's END are {}".format(nodes[n].end))
    if n != nodes[n].start[0][0]:  # no self loop
        neighbor = nodes[n].start[0]
        # checking if the neighbor is connected at start (so we have - + edge)
        # and that it only have one node from the start which is n
        if (neighbor[1] == 0) and (len(nodes[neighbor[0]].start) == 1):
            # the start of n becomes the ends of neighbor
            # and the sequence and seq_len get updated
            nodes[n].start = copy.deepcopy(nodes[neighbor[0]].end)
            # Here I need to check the new neighbors at end, and remove the merged node
            # and n to them
            for nn in nodes[neighbor[0]].end:
                # We are connected to it from start
                if nn[1] == 0:
                    nodes[nn[0]].start.remove((neighbor[0], 1))
                    nodes[nn[0]].start.append((nodes[n].id, 0))

                elif nn[1] == 1:
                    if nn[0] != neighbor[0]:
                        nodes[nn[0]].end.remove((neighbor[0], 1))
                        nodes[nn[0]].end.append((nodes[n].id, 0))
                    else:
                        nodes[n].start.remove((neighbor[0], 1))
                        nodes[n].start.append((n, 0))

            reverse = reverse_complement(nodes[neighbor[0]].seq)

            nodes[n].seq = reverse[:len(reverse) - (k - 1)] + nodes[n].seq
            nodes[n].seq_len = len(nodes[n].seq)
            nodes[neighbor[0]] = None
            none_nodes.append(neighbor[0])

            if len(nodes[n].start) == 1:
                merge_start(nodes, n, k, none_nodes)

        elif (neighbor[1] == 1) and (len(nodes[neighbor[0]].end) == 1):
            merge_end(nodes, neighbor[0], k, none_nodes)


def compact_graph(graph):
    # keeping the nodes that got merged to remove later
    none_nodes = []
    for n in graph.nodes.keys():
        # checking it's not a node that already got merged in the while loop
        if graph.nodes[n] is not None:
            # checking if it has one neighbor and it's not a self loop
            print("I am at nodes {}".format(n))
            if len(graph.nodes[n].end) == 1:
                merge_end(graph.nodes, n, graph.k, none_nodes)
            if len(graph.nodes[n].start) == 1:
                merge_start(graph.nodes, n, graph.k, none_nodes)

    # removing merged nodes
    for n in none_nodes:
        graph.remove_node(n)

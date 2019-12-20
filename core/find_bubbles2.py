import time
import sys
from .Graph2 import Bubble, BubbleChain
import pdb

"""
Pseudo code for finding bubbles
for node s in nodes:
    push s in S
    for direction in s:
        while len(s) > 0:
            pop arbitrary v from S
            v.visited = True
            if v has no children in direction:
                break
            for u in v's children in direction:
                u_parents = parents from where v connects to u
                if u == s:
                    break
                u.seen = True
                if all of u_parents are visited:
                    push u into S
            if len(S) == 1 (contains t):
                and no edge between t and s:
                    return t
                else
                    break
"""


def find_sb_alg(graph, s, direction, chain):
    """
    takes the graph and a start node s and add a bubble to the chain 
    if one is found if s was the source
    """
    # I tuples of node ids and the direction
    seen = set()
    visited = set()
    nodes_inside = []
    seen.add((s.id, direction))
    S = {(s, direction)}
    while len(S) > 0:

        v = S.pop()
        v = (v[0], v[1])
        visited.add(v[0].id)
        # v[0].visited = True  # popping a node randomly and marking as visited
        # if s.id == 167:
        #     print("node {} was popped".format((v[0].id, v[1])))
        #     pdb.set_trace()
        nodes_inside.append(v[0])

        # it's visited so it's not in the seen list anymore
        seen.remove((v[0].id, v[1]))

        # from which direction we are going we take those children
        if v[1] == 0:
            children = v[0].start
        else:
            children = v[0].end

        if len(children) == 0:
            # it's a tip
            break

        for u in children:
            # check where we entered to get children from the other side
            if u[1] == 0:
                u_child_direction = 1
                u_parents = [x[0] for x in graph.nodes[u[0]].start]
            else:
                u_child_direction = 0
                u_parents = [x[0] for x in graph.nodes[u[0]].end]

            if u[0] == s.id:
                # we are in a loop
                S = set()  # so I exit the outer loop too
                break
            # if s.id == 167:
            #     print("u is {} and its parents are {}".format(u[0], u_parents))
                
            # adding child to seen
            if u[1] == 0:
                seen.add((u[0], 1))
            else:
                seen.add((u[0], 0))

            # if s.id == 167:
            #     print("Seen nodes are {}".format(seen))

            # if all u_parents are visited then we push it into S
            #if all(graph.nodes[i].visited is True for i in u_parents):
            if all(graph.nodes[i].id in visited for i in u_parents):
                S.add((graph.nodes[u[0]], u_child_direction))

        # checking if we finished
        if (len(S) == 1) and (len(seen) == 1):
            t = S.pop()
            nodes_inside.append(t[0])

            if len(nodes_inside) == 2:
                # it's an empty bubble
                # this shouldn't happen if the graph is compacted
                break

            t[0].visited = True

            # because I'm looking in both directins I end up finding each
            # bubble twice, so I can hash the id of source and sink
            # and see if I've already found it or not
            nodes_inside.remove(s)
            nodes_inside.remove(t[0])
            bubble = Bubble(source=s, sink=t[0], inside=nodes_inside)
            # if we already found the same bubble from another directin
            if bubble not in chain:

                # adding the bubble to the node attribute
                # to help later with finding the chains and nested bubbles
                # s.bubble = -1
                # s.source.append(bubble)
                # t[0].bubbles.append(bubble)
                # t[0].sink.append(bubble)
                # for n in nodes_inside:
                #     n.bubbles.append(bubble)

                chain.add_bubble(bubble)
                

            else:
                break

    for node in nodes_inside:
        s.visited = False
        try:
            t[0].visited = False
        except:
            pass
        node.visited = False


def children_of_children(graph, children):
    """
    returns the children of the children in a list
    """

    # I need to check that each branch has the same neighbors
    # to make sure it's a simple bubble (the neighbors should be 
    # the source and sink)
    c_of_c1 = graph.nodes[children[0]].neighbors()
    c_of_c2 = graph.nodes[children[1]].neighbors()

    if c_of_c1 == c_of_c2:
        return c_of_c1
    return None


def find_b_alg(graph, s, direction, chain):
    """
    takes a graph and a start node s and adds a bubble object to the chain
    if one is found, otherwise it returns None
    This is fast for finding simple bubbles only
    """
    children = s.children(direction)

    # pdb.set_trace()
    # The source doesn't have 2 children the algorithm aborts
    if len(children) != 2:
        return None
    elif all(graph.nodes[i].visited for i in children):
        return None
    elif (len(children) == 2) and (s.id in children):
        return None

    c_of_c = children_of_children(graph, children)

    if c_of_c == None:
        return None

    if c_of_c:
        c_of_c.remove(s.id)

    if len(c_of_c) == 1:
        # what's left in c_of_c is the sink
        # can use here to start a recursive function going
        # s.visited = True
        # graph.nodes[children[0]].visited = True
        # graph.nodes[children[1]].visited = True

        # graph.nodes[c_of_c[0]].visited = True
        bubble = Bubble(source=s, 
            sink=graph.nodes[c_of_c[0]], 
            inside=[graph.nodes[children[0]],
            graph.nodes[children[1]]])

        if bubble not in chain:
            bubble.set_as_visited()
            chain.add_bubble(bubble)

        # find next bubble if exists in chain
        for d in [1,0]:
            find_b_alg(graph, graph.nodes[c_of_c[0]], d, chain)


def find_bubbles(graph):
    """
    main function for finding bubbles
    Takes a graph and fills in the bubble chains
    """
    counter = 0

    print("Sorting nodes\n")
    # sorting nodes by length
    sorted_nodes = sorted(graph.nodes, key=lambda x: graph.nodes[x].seq_len, reverse=True)
    # find_b_alg(graph, graph.nodes[167], 0, chains)
    for n in graph.nodes.values():
    # for n in [graph.nodes[5384]]:
        chain = BubbleChain()
        counter += 1
        if (counter % 100000) == 0:
            print("{} nodes have been processed".format(counter))
        if not n.visited:
            for d in [0,1]:
                # print("at node {} in direction {}".format(n.id, d))

                # if (d == 0) and (len(n.start) == 2):
                #     find_b_alg(graph, n, d, chains)
                # elif (d == 1) and (len(n.end) == 2):
                #     find_b_alg(graph, n, d, chains)
                # else:
                #find_b_alg(graph, n, d, chain)
                find_sb_alg(graph, n, d, chain)
            if len(chain) != 0:
                graph.add_chain(chain)
    # graph.bubbles = chains.bubbles


# if __name__ == "__main__":
#     start = time.time()
#     if len(sys.argv) < 3:
#         print("please give the arguments <graph_file.gfa> <k>")
#         sys.exit()

#     print("reading graph")
#     new_graph = Graph2.Graph(sys.argv[1])
#     new_graph.k = int(sys.argv[2])
#     print("Took {} seconds to read the graph".format(time.time() - start))

#     print("finding bubbles...")
#     find_bubbles(new_graph)

#     print("There were {} bubbles found".format(new_graph.n_bubbles()))
#     print("There were {} bubble chains found".format(len(new_graph.b_chains)))
#     for c in new_graph.b_chains:
#         if len(c.bubbles) > 2:
#             print(c.list_chain())
#             print(c.find_ends())

#         for b in c.bubbles:
#             new_graph.bubbles.add(b)


#     total_list = []
#     simple_b_count = 0
#     sb_count = 0
#     insertion_count = 0
#     for b in new_graph.bubbles:
#         if b.is_simple():
#             simple_b_count += 1
#         elif b.is_super():
#             sb_count += 1
#         elif b.is_insertion():
#             insertion_count += 1
#         # if (len(b.list_bubble()) > 4) or (len(b.list_bubble()) < 4):
#         #     print(b.list_bubble())
#         total_list += b.list_bubble()

#     print("Nodes covered by bubbles are {}%".format((len(set(total_list))*100)/len(new_graph.nodes)))
#     bubbles_seq = 0
#     for n in list(set(total_list)):
#         bubbles_seq += new_graph.nodes[n].seq_len - new_graph.k

#     print("Sequence covered by bubbles is {}%".format((bubbles_seq*100)/new_graph.total_seq_length()))
#     end = time.time()
#     print("It took {} to run this script".format(end - start))

#     print("Number of simple bubbles is {}".format(simple_b_count))
#     print("Number of super bubbles is {}".format(sb_count))
#     print("Number of insertion bubbles {}".format(insertion_count))

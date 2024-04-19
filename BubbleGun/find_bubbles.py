import sys
from BubbleGun.Bubble import Bubble


"""
Pseudo code for finding Super- and Simple-Bubbles
for node s in nodes:
    push s in S
    for direction in s:  # which direction to look for children
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

def find_sb_alg(graph, s, direction, only_simple=False, only_super=False):
    """
    takes the graph and a start node s and add a bubble to the chain 
    if one is found if s was the source
    """
    # I tuples of node ids and the direction
    seen = set()
    visited = set()
    nodes_inside = []
    seen.add((s.id, direction))
    # seen.add(s.id)
    S = {(s, direction)}
    while len(S) > 0:

        v = S.pop()
        v = (v[0], v[1])
        visited.add(v[0].id)

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

            # adding child to seen
            # seen.add(u[0])
            if u[1] == 0:
                seen.add((u[0], 1))
            else:
                seen.add((u[0], 0))
            # if all u_parents are visited then we push it into S
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

            # t[0].visited = True

            # because I'm looking in both directions I end up finding each
            # bubble twice, so I can hash the id of source and sink
            # and see if I've already found it or not
            nodes_inside.remove(s)
            nodes_inside.remove(t[0])
            bubble = Bubble(source=s, sink=t[0], inside=nodes_inside)

            if only_simple:
                if bubble.is_simple():
                    return bubble
            elif only_super:
                # If it's a bubble and it's not simple or an insertion
                # then it's marked as super
                if not bubble.is_simple():
                    if not bubble.is_insertion():
                        return bubble
            else:
                return bubble

    return None


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

    # The source doesn't have 2 children the algorithm aborts
    if len(children) != 2:
        return None
    elif all(graph.nodes[i].visited for i in children):
        return None
    elif (len(children) == 2) and (s.id in children):
        return None

    c_of_c = children_of_children(graph, children)

    if c_of_c is None:
        return None

    if c_of_c:
        c_of_c.remove(s.id)

    if len(c_of_c) == 1:

        bubble = Bubble(source=s,
                        sink=graph.nodes[c_of_c[0]],
                        inside=[graph.nodes[children[0]],
                                graph.nodes[children[1]]])

        if bubble not in chain:
            bubble.set_as_visited()
            chain.add_bubble(bubble)

        # find next bubble if exists in chain
        for d in [1, 0]:
            find_b_alg(graph, graph.nodes[c_of_c[0]], d, chain)


def find_bubbles(graph, only_simple=False, only_super=False, list_of_nodes=None):
    """
    main function for finding bubbles
    Takes a graph and fills in the bubble chains
    """

    if only_simple and only_super:
        print("You can't mix both only_super and only_simple, choose one or not add these arguments to detect both")
        sys.exit(1)

    if list_of_nodes is None:
        list_of_nodes = graph.nodes.values()

    # print("we are here and going into the loop")
    # counter = 0
    for n in list_of_nodes:
        # print(n.id)
        # chain = BubbleChain()
        # counter += 1
        # if (counter % 10000) == 0:
            # print(f"Process {counter} nodes for finding bubbles already")
        if not n.visited:

            for d in [0, 1]:  # looking in both direction for each node
                # find_b_alg(graph, n, d, chain)
                bubble = find_sb_alg(graph, n, d, only_simple, only_super)

                if bubble is not None:
                    graph.bubbles[bubble.key] = bubble

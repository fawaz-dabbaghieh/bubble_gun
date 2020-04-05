from .find_bubbles import find_sb_alg
from .BubbleChain import BubbleChain
import pdb


def potential_parents_in_chain(chain):
    """
    Returns a dictionary of superbubbles and the chains they belong to
    """
    poten_parents = dict()
    counter = 0
    # for chain in graph.b_chains.values():
    for b in chain.sorted:
        if b.is_super():
            poten_parents[b.key] = (chain, b)

    return poten_parents


def find_child_chains(graph, chain):
    """
    Finds superbubbles in a chain and checks if there are nested chains inside the superbubble
    """
    # all superbubbles at the beginning are potential parents
    potential_parents = potential_parents_in_chain(chain)

    for value in potential_parents.values():
        sb = value[1]
        for n in sb.inside:
            n.visited = False

        for n in sb.inside:
            new_chain = BubbleChain()
            if not n.visited:

                for d in [0, 1]:
                    # find_b_alg(graph, n, d, chain)
                    find_sb_alg(graph, n, d, new_chain, False)
                if len(new_chain) != 0:
                    # parent child information can be added here
                    new_chain.find_ends()
                    # graph.child_parent[new_chain._BubbleChain__key()] = value
                    graph.child_parent[chain] = value

                    # calling again in case the nested chain had more nested chains
                    find_child_chains(graph, new_chain)

                    graph.add_chain(new_chain)

                    for n in new_chain.list_chain(ids=False):
                        n.visited = True


def find_children(graph):
    """
    Finding all smaller chains inside superbubbles
    """
    chains = list(graph.b_chains)
    for chain in chains:
        find_child_chains(graph, chain)

    # adding ids
    b_counter = 1
    chain_counter = 1
    for chain in graph.b_chains:
        chain.id = chain_counter
        if chain.id == 0:
            pdb.set_trace()
        for b in chain.sorted:
            b.id = b_counter
            b_counter += 1
        chain_counter += 1
    # for each superbubble, I run the chain detection algorithm again
    # the bubble chains I save their keys, the chain is not in graph.b_chains I add them there
    # I check if the new chains recursively have any superbubbles, then I run the thing again
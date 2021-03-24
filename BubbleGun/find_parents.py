import logging
from BubbleGun.find_bubbles import find_sb_alg
import pdb

"""
Sort all Sbs from biggest to smallest
then starting from biggest, find nested bubbles, assign parent to be the sb I started with
repeat for each sb

In theory, the bubbles in one chain should have the same parent sb, which should solve the problem
"""


def list_in_list(list1, list2):
    for n in list1:
        if n not in list2:
            return False
    return True


def find_parents(graph):
    all_sbs = [x for x in graph.bubbles.values() if x.is_super()]

    # todo: check this with a bigger example
    all_sbs = sorted(all_sbs, key=lambda x: len(x.inside))
    all_sbs.reverse()

    """
    Best way I can do this is by turning graph.bubbles into a dictionary
    Then it's easier to change the values with bubbles that have a parent id 
    """
    for sb in all_sbs:
        list_of_nodes = sb.inside
        inside_bubbles = set()
        for n in list_of_nodes:
            for d in [0, 1]:
                bubble = find_sb_alg(graph, n, d)
                if bubble is not None:
                    # bubble.parent_sb = sb
                    if bubble.key in graph.bubbles:
                        graph.bubbles[bubble.key].parent_sb = sb.id
                        graph.bubbles[bubble.key].parent_chain = sb.chain_id
                    # print(id(bubble))
                    # pdb.set_trace()

    for chain in graph.b_chains:
        for b in chain.bubbles:
            if b.parent_sb != 0:
                chain.parent_sb = b.parent_sb
                chain.parent_chain = b.parent_chain
                break

import logging
import pdb
from BubbleGun.BubbleChain import BubbleChain


def connect_bubbles(graph):
    """
    takes a graph object and connects the individual bubbles into chains and add them back to graph object
    """

    ids_to_bubbles = dict()
    for b in graph.bubbles.values():
        if b.source.id not in ids_to_bubbles:
            ids_to_bubbles[b.source.id] = [b]
        else:
            ids_to_bubbles[b.source.id].append(b)

        if b.sink.id not in ids_to_bubbles:
            ids_to_bubbles[b.sink.id] = [b]
        else:
            ids_to_bubbles[b.sink.id].append(b)

    starting_nodes = [x for x in ids_to_bubbles if len(ids_to_bubbles[x]) == 1]

    # a source or a sink can be part of two bubbles at most
    # so lists in ids_to_bubbles can only be 1 or 2 in length
    for n in starting_nodes:
        chain = BubbleChain()
        if ids_to_bubbles[n]:
            current_b = ids_to_bubbles[n][0]
        else:
            continue
        current_n = n
        while True:

            if current_n == current_b.source.id:
                next_n = current_b.sink.id
            else:
                next_n = current_b.source.id

            ids_to_bubbles[next_n].remove(current_b)

            chain.add_bubble(current_b)

            if len(ids_to_bubbles[next_n]) < 1:
                break

            current_b = ids_to_bubbles[next_n][0]  # this has only one bubble
            current_n = next_n

        if len(chain) != 0:
            chain.find_ends()
            graph.add_chain(chain)  # get sorted and ends found when added to graph

    # filling bubbles and chains ids
    b_counter = 1
    chain_counter = 1
    for chain in graph.b_chains:
        chain.id = chain_counter

        for b in chain.sorted:
            b.id = b_counter
            b.chain_id = chain.id
            b_counter += 1
        chain_counter += 1

    # pdb.set_trace()

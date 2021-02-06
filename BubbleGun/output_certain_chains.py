import json
import os
import sys
import pdb


def write_certain_chains(json_file, graph, chain_ids, output_file):
    """
    Output certain chains based on their ids
    """

    set_of_nodes = set()
    chain_ids = set(chain_ids)
    if not os.path.exists(json_file):
        print("File {} does not exists, make sure tha path is correct".format(json_file))
        sys.exit(1)

    with open(json_file, "r") as in_file:
        for line in in_file:
            chains = json.loads(line)
            for c_id in chain_ids:
                if c_id not in chains:
                    continue

                wanted_chain = chains[c_id]
                set_of_nodes = set_of_nodes.union(set(wanted_chain['ends']))
                for bubble in wanted_chain['bubbles']:
                    set_of_nodes = set_of_nodes.union(set(bubble['ends']))
                    set_of_nodes = set_of_nodes.union(set(bubble['inside']))

    graph.write_graph(set_of_nodes=set_of_nodes, output_file=output_file)

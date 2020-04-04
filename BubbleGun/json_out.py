import json
import pdb


def json_out(graph, output):
    # For each chain I output each bubble's ends and insides
    # First I'll give each bubble an id so the children chain can have a parent id
    # now the parent is just a pointer to a sb object and a chain object
    b_counter = 1
    chain_counter = 1
    for chain in graph.b_chains.values():
        chain.id = chain_counter
        for b in chain.sorted:
            b.id = b_counter
            b_counter += 1
        chain_counter += 1

    # pdb.set_trace()
    output_f = open(output, "w")
    for child_chain_key, parent_info in graph.child_parent.items():
        chain_line = dict()
        chain_line['id'] = graph.b_chains[child_chain_key].id
        chain_line['ends'] = graph.b_chains[child_chain_key].ends
        chain_line['bubbles'] = []
        chain_line['parent_chain'] = graph.b_chains[parent_info[0]].id
        chain_line['parent_sb'] = parent_info[1].id
        for bubble in graph.b_chains[child_chain_key].sorted:
            line = dict()
            if bubble.is_simple():
                line['type'] = 'simple'
            elif bubble.is_super():
                line['type'] = 'super'
            else:
                line['type'] = 'insertion'

            line['id'] = bubble.id
            line["ends"] = [bubble.source.id, bubble.sink.id]
            line['inside'] = [x.id for x in bubble.inside]
            chain_line['bubbles'].append(line)

        output_f.write(json.dumps(chain_line) + "\n")

    for chain_key, chain in graph.b_chains.items():
        # The chains that are not nested
        if chain_key not in graph.child_parent:
            chain_line = dict()
            chain_line['id'] = chain.id
            chain_line['ends'] = chain.ends
            chain_line['bubbles'] = []
            for bubble in chain.sorted:
                line = dict()

                if bubble.is_simple():
                    line['type'] = 'simple'
                    # line['id'] = bubble.inside[0].which_b

                elif bubble.is_super():
                    line['type'] = 'super'
                    # line['id'] = bubble.inside[0].which_sb

                else:
                    line['type'] = 'insertion'
                    # line['id'] = bubble.inside[0].which_s

                line['id'] = bubble.id
                line["ends"] = [bubble.source.id, bubble.sink.id]
                line['inside'] = [x.id for x in bubble.inside]

                chain_line['bubbles'].append(line)

            output_f.write(json.dumps(chain_line) + "\n")

    output_f.close()

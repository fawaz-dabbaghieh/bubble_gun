import json


def json_out(graph, output):
    # For each chain I output each bubble's ends and insides
    # First I'll give each bubble an id so the children chain can have a parent id
    # now the parent is just a pointer to a sb object and a chain object
    # b_counter = 1
    # chain_counter = 1
    # for chain in graph.b_chains.values():
    #     chain.id = chain_counter
    #     for b in chain.sorted:
    #         b.id = b_counter
    #         b_counter += 1
    #     chain_counter += 1

    # pdb.set_trace()
    output_f = open(output, "w")
    # output_f.write("[\n")
    json_out = dict()
    # # I am writing the nested chains first
    # for child_chain_key, parent_info in graph.child_parent.items():
    #     chain_line = dict()
    #
    #     chain_line['chain_id'] = child_chain_key.id
    #     chain_line['ends'] = child_chain_key.ends
    #     chain_line['bubbles'] = []
    #     chain_line['parent_chain'] = parent_info[0].id
    #     chain_line['parent_sb'] = parent_info[1].id
    #     for bubble in child_chain_key.sorted:
    #         line = dict()
    #         if bubble.is_simple():
    #             line['type'] = 'simple'
    #         elif bubble.is_super():
    #             line['type'] = 'super'
    #         else:
    #             line['type'] = 'insertion'
    #
    #         line['id'] = bubble.id
    #         line["ends"] = [bubble.source.id, bubble.sink.id]
    #         line['inside'] = [x.id for x in bubble.inside]
    #         chain_line['bubbles'].append(line)
    #
    #     json_out[child_chain_key.id] = chain_line
    #     # output_f.write(json.dumps(chain_line) + ",\n")
    # not nested chains

    for chain in graph.b_chains:
        # The chains that are not nested
        chain_line = dict()
        chain_line['chain_id'] = chain.id
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

        if bubble.parent_sb != 0:
            chain_line['parent_sb'] = bubble.parent_sb
            chain_line['parent_chain'] = bubble.parent_chain

        json_out[chain.id] = chain_line
            # output_f.write(json.dumps(chain_line) + ",\n")
    output_f.write(json.dumps(json_out))
    # output_f.write("]")
    output_f.close()

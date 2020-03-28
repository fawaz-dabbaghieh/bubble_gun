import json
import pdb

def json_out(graph, output):
    # For each chain I output each bubble's ends and insides
    chain_id = 1
    output_f = open(output, "w")

    for chain in graph.b_chains:
        chain_line = dict()
        chain_line['id'] = chain_id
        chain_line['ends'] = chain.ends
        chain_line['bubbles'] = []
        for bubble in chain.sorted:
            line = dict()

            if bubble.is_simple():
                line['type'] = 'simple'
                line['id'] = bubble.inside[0].which_b

            elif bubble.is_super():
                line['type'] = 'super'
                line['id'] = bubble.inside[0].which_sb

            else:
                line['type'] = 'insertion'
                line['id'] = bubble.inside[0].which_s

            line["ends"] = [bubble.source.id, bubble.sink.id]
            line['inside'] = [x.id for x in bubble.inside]
            if len(bubble.inside) > 2:
                pdb.set_trace()
            chain_line['bubbles'].append(line)

        output_f.write(json.dumps(chain_line) + "\n")
        chain_id += 1

    output_f.close()

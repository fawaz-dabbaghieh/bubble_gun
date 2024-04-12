from BubbleGun.path_extractor import sequence_extractor


def write_bubbles(graph, output_path):
    out_file = open(output_path, "w")

    for chain in graph.b_chains:
        for bubble in chain.sorted:
            if not bubble.is_simple():
                continue

            first_path = [bubble.source.id, bubble.inside[0].id, bubble.sink.id]
            seq1 = sequence_extractor(graph, first_path)
            second_path = [bubble.source.id, bubble.inside[1].id, bubble.sink.id]
            seq2 = sequence_extractor(graph, second_path)

            read_name1 = ">bubble_" + str(bubble.id) + "_allele_1" + "_chain_" + str(chain.id)
            read_name2 = ">bubble_" + str(bubble.id) + "_allele_2" + "_chain_" + str(chain.id)

            out_file.write(read_name1 + "\n")
            out_file.write(seq1 + "\n")
            out_file.write(read_name2 + "\n")
            out_file.write(seq2 + "\n")

    out_file.close()

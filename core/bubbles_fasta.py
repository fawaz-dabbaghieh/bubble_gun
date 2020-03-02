def write_fasta(fa_path, graph):
    out_file = open(fa_path, "w")
    for chain in graph.b_chains:
        for bubble in chain.bubbles:
            allele = 1
            for branch in bubble.inside:
                read_name = ">bubble_" + str(branch.which_b) + "_allele_" + str(allele) + "_chain_" + str(branch.which_chain) + "_node_" + str(branch.id) + "_km_" + str(branch.coverage)
                allele += 1
                out_file.write(read_name + "\n")
                out_file.write(branch.seq + "\n")

    out_file.close()
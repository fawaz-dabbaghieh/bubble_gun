def write_fasta(fa_path, graph):
    out_file_bubbles = open(fa_path, "w")
    other_file = "other_nodes" + fa_path
    out_file_other = open(other_file, "w")

    for chain in graph.b_chains:
        for bubble in chain.bubbles:
            allele = 1
            for branch in bubble.inside:
                read_name = ">bubble_" + str(branch.which_b) + "_allele_" + str(allele) + "_chain_" + str(branch.which_chain) + "_km_" + str(branch.coverage) + "_node_" + str(branch.id)
                allele += 1
                out_file_bubbles.write(read_name + "\n")
                out_file_bubbles.write(branch.seq + "\n")

    for n in graph.nodes.values():
        if (n.which_chain != 0) and (n.which_allele == -1):
            read_name = ">node_" + str(n.id) + "_chain_" + str(n.which_chain)
            out_file_other.write(read_name + "\n")
            out_file_other.write(n.seq + "\n")
        elif n.which_chain == 0:
            read_name = ">node_" + str(n.id) + "_chain_0"
            out_file_other.write(read_name + "\n")
            out_file_other.write(n.seq + "\n")

    out_file_bubbles.close()
    out_file_other.close()

from BubbleGun.path_extractor import sequence_extractor
import pdb


def output_chains_fasta(graph):

    # Chain ids should be from 1 to len(graph.b_chains)
    chain_id = 1
    hap1_file = open("haplotype1.fasta", "w")
    hap2_file = open("haplotype2.fasta", "w")
    # chain_counter = 1
    for chain in graph.b_chains:
        hap1 = []
        hap2 = []
        if len(chain.sorted) == 0:
            chain.sort()

        # very hacky stuff, don't judge, I wrote it on a train from Dusseldorf to Saarbrucken
        # should do it with topological sorting but I'm too tired
        for b in chain.sorted:
            if len(hap1) == 0:
                # chain_id = b.source.which_chain
                hap1.append(chain.ends[0])
                hap2.append(chain.ends[0])
                hap1.append(b.inside[0].id)
                hap2.append(b.inside[1].id)
                if hap1[len(hap1) - 2] == b.source.id:
                    hap1.append(b.sink.id)
                    hap2.append(b.sink.id)
                else:
                    hap1.append(b.source.id)
                    hap2.append(b.source.id)

            else:
                if hap1[-1] == b.source.id:
                    hap1.append(b.inside[0].id)
                    hap2.append(b.inside[1].id)
                    hap1.append(b.sink.id)
                    hap2.append(b.sink.id)
                else:
                    hap1.append(b.inside[0].id)
                    hap2.append(b.inside[1].id)
                    hap1.append(b.source.id)
                    hap2.append(b.source.id)

        seq1 = sequence_extractor(graph, hap1)
        if len(seq1) == 0:
            pdb.set_trace()
        read_name = ">chain_" + str(chain_id) + "_hap1"
        hap1_file.write(read_name + "\n")
        hap1_file.write(seq1 + "\n")

        seq2 = sequence_extractor(graph, hap2)
        read_name = ">chain_" + str(chain_id) + "_hap2"
        hap2_file.write(read_name + "\n")
        hap2_file.write(seq2 + "\n")
        chain_id += 1

    hap1_file.close()
    hap2_file.close()

from core import Graph2, Node2, functions
import pdb


print("importing a GFA file...")
graph_gfa = Graph2.Graph("../10565_9516_long_reads.181.untipped.compacted.gfa")
print("finding chains")
graph_gfa.find_chains()
print(graph_gfa)


print("\n\nimporting the same GFA file as VG...")
graph_vg = Graph2.Graph("../10565_9516_long_reads.181.untipped.compacted.vg")
print("finding chains")
graph_vg.find_chains()
print(graph_vg)

pdb.set_trace()
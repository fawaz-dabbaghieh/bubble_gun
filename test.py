from core.Graph import Graph
import pdb
import sys


# pdb.set_trace()
print("Reading a Graph file...")
print("compacting graph")
graph_gfa.compact()
print("finding chains")
graph_gfa.find_chains()
print(graph_gfa)


# print("\n\nimporting the same GFA file as VG...")
# graph_vg = Graph2.Graph(sys.argv[2])
# print("finding chains")
# graph_vg.find_chains()
# print(graph_vg)

# pdb.set_trace()

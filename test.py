from core import Graph2, functions
import pdb
import sys


# pdb.set_trace()
print("Reading a Graph file...")
graph_gfa = Graph2.Graph(sys.argv[1])
print("finding chains")
graph_gfa.find_chains()
print(graph_gfa)


# print("\n\nimporting the same GFA file as VG...")
# graph_vg = Graph2.Graph(sys.argv[2])
# print("finding chains")
# graph_vg.find_chains()
# print(graph_vg)

# pdb.set_trace()
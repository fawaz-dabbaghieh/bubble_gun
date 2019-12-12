import os
import sys
from Graph2 import Graph, BubbleChain
from find_bubbles2 import find_bubbles
from functions import calculate_n50
import pdb


def check_chain(bubble):
	x = set(bubble.source.source + bubble.source.sink
		 + bubble.sink.sink+ bubble.sink.source)
	x = list(x)
	return list(x)


table_header = [x for x in "k Value,"
"Number of Nodes,Sequence Length,N50,Number of Components,Biggest Comp (nodes)"
",Biggest Comp (nodes%),Biggest Comp (seq),Biggest Comp (seq%)".split(",")]
stats = [table_header]

if len(sys.argv) < 3:
	print("Please give the argument <graph.gfa> <k>")
	sys.exit()

graph = Graph(sys.argv[1])
graph.k = int(sys.argv[2])
find_bubbles(graph)
some_chain = BubbleChain()

for b in graph.bubbles[1:10]:
	some_chain.add_bubble(b)

graph.b_chains.append(some_chain)
pdb.set_trace()
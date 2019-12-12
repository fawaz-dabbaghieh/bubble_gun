import time
import sys
from Graph2 import Graph, Bubble

"""
Pseudo code
for node s in nodes:
	push s in S
	for direction in s:
		while len(s) > 0:
			pop arbitrary v from S
			v.visited = True
			if v has no children in direction:
				break
			for u in v's children in direction:
				u_parents = parents from where v connects to u
				if u == s:
					break
				u.seen = True
				if all of u_parents are visited:
					push u into S
			if len(S) == 1 (contains t):
				and no edge between t and s:
					return t
				else
					break
"""

def find_sb_alg(graph, s, direction, list_of_b):
	"""
	takes the graph and a start node s and returns a bubble object
	if s was the source
	"""
	# I tuples of node ids and the direction
	seen = set()
	nodes_inside = []
	seen.add((s.id, direction))
	S = {(s, direction)}
	while len(S) > 0:
		v = S.pop()
		v = (v[0], v[1])
		v[0].visited = True  # popping a node randomly and marking as visited
		nodes_inside.append(v[0])

		# it's visited so it's not in the seen list anymore
		seen.remove((v[0].id, v[1]))

		# which direction we are going we take those children
		if v[1] == 0:
			children = v[0].start
		else:
			children = v[0].end

		if len(children) == 0:
			# it's a tip
			break
		for u in children:
			# so we came to u from 0 we need to exit from 1
			if u[1] == 0:
				u_child_direction = 1
				u_parents = [x[0] for x in graph.nodes[u[0]].start]
			else:
				u_child_direction = 0
				u_parents = [x[0] for x in graph.nodes[u[0]].end]

			if u[0] == s.id:
				# we are in a loop
				S = set()
				break

			# adding child to seen
			if u[1] == 0:
				seen.add((u[0], 1))
			else:
				seen.add((u[0], 0))

			# if all u_parents ts are visited then we push it into S
			if all(graph.nodes[i].visited is True for i in u_parents):
				S.add((graph.nodes[u[0]], u_child_direction))

		# checking if we finished
		if (len(S) == 1) and (len(seen) == 1):
			t = S.pop()
			nodes_inside.append(t[0])

			if len(nodes_inside) == 2:
				# it's an empty bubble
				# this shouldn't happen if the graph is compacted
				break

			t[0].visited = True

			# because I'm looking in both directins I end up finding each
			# bubble twice, so I can hash the id of source and sink
			# and see if I've already found it or not
			nodes_inside.remove(s)
			nodes_inside.remove(t[0])
			bubble = Bubble(source=s, sink=t[0], inside=nodes_inside)
			# if we already found the same bubble from another directin
			if bubble not in list_of_b:

				# adding the bubble to the node attribute
				# to help later with finding the chains and nested bubbles
				s.bubbles.append(bubble)
				s.source.append(bubble)
				t[0].bubbles.append(bubble)
				t[0].sink.append(bubble)
				for n in nodes_inside:
					n.bubbles.append(bubble)

				list_of_b.append(bubble)

			else:
				break

	for node in nodes_inside:
		s.visited = False
		try:
			t[0].visited = False
		except:
			pass
		node.visited = False


def find_bubbles(graph):
	counter = 0

	for n in graph.nodes.values():
		counter += 1
		if (counter % 100000) == 0:
			print("{} nodes have been processed".format(counter))
		if not n.visited:
			for d in [0,1]:
				find_sb_alg(graph, n, d, graph.bubbles)


if __name__ == "__main__":
	start = time.time()
	if len(sys.argv) < 3:
		print("please give the arguments <graph_file.gfa> <k>")
		sys.exit()

	print("reading graph")
	new_graph = Graph(sys.argv[1])
	new_graph.k = int(sys.argv[2])
	print("Took {} seconds to read the graph".format(time.time() - start))

	print("finding bubbles...")
	find_bubbles(new_graph)

	print("There were {} bubbles found".format(len(new_graph.bubbles)))

	total_list = []
	for b in new_graph.bubbles:
		if (len(b.list_bubble()) > 4) or (len(b.list_bubble()) < 4):
			print(b.list_bubble())
		total_list += b.list_bubble()

	print("Nodes covered by bubbles are {}%".format((len(set(total_list))*100)/len(new_graph.nodes)))
	bubbles_seq = 0
	for n in list(set(total_list)):
		bubbles_seq += new_graph.nodes[n].seq_len - new_graph.k

	print("Sequence covered by bubbles is {}%".format((bubbles_seq*100)/new_graph.total_seq_length()))
	end = time.time()
	print("It took {} to run this script".format(end - start))
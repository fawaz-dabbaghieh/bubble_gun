import os
import sys
from Node2 import Node
import Graph2


def reverse_complement(dna):
	complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A'}
	return ''.join([complement[base] for base in dna[::-1]])



def write_gfa(nodes, k, list_of_nodes=None, ignore_nodes=None, output_file="output_file.gfa",
			  append=False, modified=False):
	"""
	:param nodes: Dictionary of nodes object.
	:param list_of_nodes: A list of node ids of the path or nodes we want to generate a GFA file for.
	:param k: overlap between two nodes.
	:param ignore_nodes: nodes that I don't need to write their edges out
	:param output_file: path to output file
	:param append: if I want to append to a file instead of rewriting it
	:param modified: To write my modified GFA file format instead of the standard GFA
	:return: writes a gfa file
	"""

	if ignore_nodes is None:
		ignore_nodes = set()

	if list_of_nodes is None:
		list_of_nodes = list(nodes.keys())
	# if os.path.exists(output_file):
		# print("File already exists, do you want to overwrite. y/n: ")
		# choice = input().lower()
		# if choice == "y":
		#	 output_file = output_file
		# elif choice == "n":
		#	 sys.exit()
		# else:
		#	 print("invalid choice")
		#	 sys.exit()
	if append is False:
		f = open(output_file, "w+")
	else:
		if os.path.exists(output_file):
			f = open(output_file, "a")
		else:
			print("the output file {} does not exist".format(output_file))
			return None

	for n1 in list_of_nodes:
		# writing nodes in gfa file
		if modified:
			node = nodes[n1]
			# todo for now I don't care to which sb the node belongs, I just care about simple bubbles for phasing
			specification = str(":".join((str(node.which_chain), str(0),
										  str(node.which_b), str(node.which_allele))))
			if nodes[n1].seq == "":
				line = str("\t".join(("S", str(n1), str("A" * nodes[n1].seq_len), specification)))
			else:
				line = str("\t".join(("S", str(n1), nodes[n1].seq, specification)))

			f.write(line + "\n")
		else:
			if nodes[n1].seq == "":
				line = str("\t".join(("S", str(n1), str("A" * nodes[n1].seq_len))))
			else:
				line = str("\t".join(("S", str(n1), nodes[n1].seq)))

			f.write(line + "\n")

		# getting the edges
		edges = []
		overlap = str(int(k) - 1) + "M\n"
		if n1 in ignore_nodes:
			continue

		for n in nodes[n1].start:
			# I think the ignore nodes should be here
			# because I want to ignore the end nodes of a bubble branch
			# I only need the node, not it's edges
			# Or maybe when I separate the branches, remove the edges to the rest of the graph
			# checking if the node was removed from graph.nodes at some point then I don't write that edge
			# also checking if I need to ignore the edges here
			if n[0] in nodes:  # and (n[0] not in ignore_nodes):
				if n[1] == 0:
					edge = str("\t".join(("L", str(n1), "-", str(n[0]), "+", overlap)))
					edges.append(edge)
				else:
					edge = str("\t".join(("L", str(n1), "-", str(n[0]), "-", overlap)))
					edges.append(edge)

		for n in nodes[n1].end:
			if n[0] in nodes:  # and (n[0] not in ignore_nodes):
				if n[1] == 0:
					edge = str("\t".join(("L", str(n1), "+", str(n[0]), "+", overlap)))
					edges.append(edge)
				else:
					edge = str("\t".join(("L", str(n1), "+", str(n[0]), "-", overlap)))
					edges.append(edge)

		for e in edges:
			f.write(e)

	f.close()



def read_gfa(gfa_file_path, modified=False):
	"""
	:param gfa_file_path: gfa graph file.
	:param modified: if I'm reading my modified GFA with extra information for the nodes
	:return: Dictionary of node ids and Node objects.
	"""
	if not os.path.exists(gfa_file_path):
		print("the gfa file path you gave does not exists, please try again!")
		sys.exit()

	nodes = dict()
	edges = []
	with open(gfa_file_path, "r") as lines:
		for line in lines:
			if line.startswith("S"):
				if modified:
					line = line.split("\t")
					n_id = int(line[1])
					n_len = len(line[2])
					nodes[n_id] = Node(n_id)
					nodes[n_id].seq_len = n_len
					nodes[n_id].seq = str(line[2])
					specifications = str(line[3])
					specifications = specifications.split(":")
					nodes[n_id].which_chain = int(specifications[0])
					nodes[n_id].which_sb = int(specifications[1])
					nodes[n_id].which_b = int(specifications[2])
					nodes[n_id].which_allele = int(specifications[3])

				else:

					line = line.split()
					n_id = int(line[1])
					n_len = len(line[2])
					nodes[n_id] = Node(n_id)
					nodes[n_id].seq_len = n_len
					nodes[n_id].seq = str(line[2])

			elif line.startswith("L"):
				edges.append(line)

	for e in edges:
		line = e.split()

		k = int(line[1])
		neighbor = int(line[3])
		if line[2] == "-":
			from_start = True
		else:
			from_start = False

		if line[4] == "-":
			to_end = True
		else:
			to_end = False

		if from_start is True and to_end is True:  # from start to end L x - y -
			if (neighbor, 1) not in nodes[k].start:
				nodes[k].start.append((neighbor, 1))
			if (k, 0) not in nodes[neighbor].end:
				nodes[neighbor].end.append((k, 0))

		elif from_start is True and to_end is False:  # from start to start L x - y +

			if (neighbor, 0) not in nodes[k].start:
				nodes[k].start.append((neighbor, 0))

			if (k, 0) not in nodes[neighbor].start:
				nodes[neighbor].start.append((k, 0))

		elif from_start is False and to_end is False:  # from end to start L x + y +
			if (neighbor, 0) not in nodes[k].end:
				nodes[k].end.append((neighbor, 0))

			if (k, 1) not in nodes[neighbor].start:
				nodes[neighbor].start.append((k, 1))

		elif from_start is False and to_end is True:  # from end to end L x + y -
			if (neighbor, 1) not in nodes[k].end:
				nodes[k].end.append((neighbor, 1))

			if (k, 1) not in nodes[neighbor].end:
				nodes[neighbor].end.append((k, 1))

	return nodes


def calculate_n50(graph):
	list_of_lengths = []
	for n in graph.nodes.values():
		list_of_lengths.append(n.seq_len)
	list_of_lengths = sorted(list_of_lengths)
	new_list = []
	for x in list_of_lengths:
		new_list += [x]*x
	if len(new_list) % 2 ==0:
		medianpos = int(len(new_list)/2)
		return float(new_list[medianpos] + new_list[medianpos-1])/2
	else:
		medianpos = int(len(new_list)/2)
		return new_list[medianpos]


def check_chains(bubble):
	x = set(bubble.source.source + bubble.source.sink
		 + bubble.sink.sink+ bubble.sink.source)
	return list(x)


def find_chains(graph):
	
	for bubble in graph.bubbles:
		chain = Graph2.BubbleChain()
		queue = [bubble]
		while queue:
			current_b = queue.pop()
			neighbors = check_chains(current_b)
			current_b.visited = True
			for b in  neighbors:
				if not b.visited:
					queue.apend(b)
					
			chain.add_bubble(current_b)
			
	visited_b = []

import os
from Node2 import Node

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


class Bubble:
	"""
	Bubble object that has the important information about a bubble
	"""

	def __init__(self, source, sink, inside):
		self.source = source
		self.sink = sink
		self.inside = inside
		self.visited = False  # I need this when finding chains

	
	def __len__(self):
		"""
		overloading the length function
		"""
		return (len(self.inside) + 2)


	def __key(self):
		source = int(self.source.id)
		sink = int(self.sink.id)
		if source > sink:
			return (source, sink)
		return (sink, source)

	# I need to hash the bubbles because I can find the same bubble
	# twice as I'm coming from both directions
	# this way I can avoid adding it twice to the list of bubbles
	def __hash__(self):
		return hash(self.__key())


	def __eq__(self, other):
		return self.__key() == other.__key()


	def __ne__(self, other):
		return not self.__eq__(other)


	def list_bubble(self):
		""""
		returns a list of node ids that make up the bubble
		"""
		node_list = [self.source.id, self.sink.id]
		for n in self.inside:
			node_list.append(n.id)
		return node_list

	def node_length(self):
		"""
		returns how many nodes in the bubble including source and sink
		"""
		return (len(self.inside) + 2)  # +2 for source and sink


	def seq_length(self, k):
		"""
		returns the total sequence in the bubble
		"""
		total_seq = self.source.seq_len + self.sink.seq_len - 2*k
		for n in self.inside:
			total_seq += n.seq_len - k
		return total_seq


	def is_simple(self):
		"""
		returns true if it's a simple bubble
		"""
		if len(self.inside) == 2:
			return True
		return False


	def is_insertion(self):
		"""
		returns true if it's an insertion
		i.e. bubble with one branch
		"""
		if len(self.inside) == 1:
			return True
		return False


	def is_super(self):
		"""
		returns true if it's a superbubble
		"""
		if len(self.inside) > 2:
			return True
		return False


class BubbleChain:
	"""
	BubbleChain object which is a list of bubbles object
	"""

	def __init__(self):
		self.bubbles = []


	def __len__(self):
		"""
		overloading the length functino
		"""
		return len(self.bubbles)


	def add_bubble(self, bubble):
		"""
		adds a bubble object to the chain
		"""
		self.bubbles.append(bubble)


	def list_chain(self):
		"""
		return all nodes in the chain as a list of node objects
		"""
		c_list = []
		for b in self.bubbles:
			c_list += [b.source.id, b.sink.id] + [x.id for x in b.inside]
		return list(set(c_list))  # set to remove redundant sources and sinks


	def node_length(self):
		"""
		returns how many nodes there are in the chain
		"""
		return len(self.list_chain())


	def seq_length(self, k):
		"""
		returns sequence length covered by the chain
		"""
		c_list = []
		for b in self.bubbles:
			c_list += [b.source, b.sink] + b.inside
		c_list = list(set(c_list))

		total_seq = 0
		for n in c_list:
			total_seq += n.seq_len - k
		return total_seq


	def find_ends(self):
		"""
		returns the ends of the chain
		"""
		ends = []
		all_ends = []
		for b in self.bubbles:
			all_ends.append(b.source.id)
			all_ends.append(b.sink.id)
		for n in all_ends:
			if all_ends.count(n) == 1:
				ends.append(n)
		return ends


	#def sort(self):


class Graph:
	"""
	Graph object containing the important information about the graph
	"""
	def __init__(self, graph_file):
		self.nodes = read_gfa(graph_file)
		self.b_chains = []  # list of BubbleChain objects
		self.bubbles = []
		self.k = 0


	def __len__(self):
		"""
		overloading the length function
		"""
		return (len(self.nodes))


	def __str__(self):
		"""
		overloading the string function for printing
		"""
		return "The graph has {} Nodes and {} bubble and {} chains".format(
			len(self.nodes), len(self.bubbles), len(self.b_chains))


	# def __repr__(self):
	# 	"""
	# 	overloading the string function for printing
	# 	"""
	# 	return "The graph has {} Nodes and {} bubble and {} chains".format(
	# 		len(self.nodes), len(self.bubbles), len(self.b_chains))

	def add_chain(self, chain):
		self.b_chains.append(chain)


	def total_seq_length(self):
		"""
		returns total sequence length
		"""
		total = 0
		for n in self.nodes.values():
			total += n.seq_len - self.k
		return total


	def longest_chain_node(self):
		"""
		returns the longest bubble chain bubble wise
		In case there are more than on longest chain it
		returns the first one found
		"""
		lengths_list = [x.node_length() for x in self.b_chains]
		m = max(lengths_list)
		return self.b_chains[[i for i, j in enumerate(lengths_list) if j == m][0]]


	def longest_chain_seq(self):
		"""
		returns the longest bubble chain sequence wise
		In case there are more than on longest chain it
		returns the first one found
		"""
		lengths_list = [x.seq_length(k=self.k) for x in self.b_chains]
		m = max(lengths_list)
		return self.b_chains[[i for i, j in enumerate(lengths_list) if j == m][0]]


	def nodes_in_chains(self):
		"""
		returns the number of nodes that are part of a bubble chain
		"""
		n_in_c = 0
		for chain in self.b_chains:
			n_in_c += chain.node_length()

		return n_in_c


	def seq_in_chains(self):
		"""
		returns how much sequence ther are in the bubble chains
		"""
		s_in_c = 0
		for chain in self.b_chains:
			s_in_c += chain.seq_length(k=self.k)

		return s_in_c


	def chain_cov_node(self):
		"""
		returns the percentage the nodes in chains covered
		"""
		n_in_c = self.nodes_in_chains()
		return float((n_in_c*100)/len(self.nodes))


	def chain_cov_seq(self):
		"""
		returns the percentage the sequences in chains covered
		"""
		s_in_c = self.seq_in_chains()

		return float((s_in_c*100)/self.total_seq_length())


	def num_single_bubbles(self):
		"""
		return the number of chains that has only one bubble
		"""
		nsb = 0
		for chain in self.b_chains:
			if len(chain) == 1:
				nsb += 1
		return nsb
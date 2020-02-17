from core.vg_pb2 import Alignment
from core.functions import current_time
from core.graph_io import read_gfa
from core.Node import Node
import stream
import pdb

def build_reads_dict(gam_file_path):
	all_reads = dict()

	# reading gam file
	with stream.open(str(gam_file_path), "rb") as in_stream:
		counter = 0
		for data in in_stream:
			counter += 1

			if (counter % 1000000) == 0:
				print("[{}] {} reads processed".format(current_time(), counter))
				# return all_reads

			align = Alignment()
			align.ParseFromString(data)

			# skipping alignments with less than 200 base pairs
			if len(align.sequence) < 200:
				continue

			# I need to add something related to comparing alignments
			# to the same chain
			# if one alignment to the same chain is longer than another
			# I keep the longer one
			if align.name not in all_reads:
				all_reads[align.name] = []

			for m in align.path.mapping:
				n_id = int(m.position.node_id)
				all_reads[align.name].append(n_id)

			# pdb.set_trace()

	return all_reads
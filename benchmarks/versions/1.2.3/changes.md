# 1.2.3

- Reduced Python overhead in the packed bubble finder inner loop by operating on encoded side handles instead of `(node, direction)` tuples.
- Avoided rebuilding full `PackedBubble` objects during packed parent finding, since that path only needs the bubble key.
- Simplified packed bubble classification checks to avoid unnecessary temporary set/list allocations.
- Recorded a new `chr22_graph.gfa` benchmark with identical output: wall time improved to 47.05s and max RSS dropped to 1907648 KB.

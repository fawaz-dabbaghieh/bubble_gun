# 1.2.1

- Added a new `PackedGraph` implementation with dense internal integer node indices.
- Stored oriented topology in packed side-adjacency arrays for read-only traversal experiments.
- Added tests for packed graph ID mapping, metadata loading, and adjacency equivalence on a small GFA.
- Added a versioned benchmark runner and baseline benchmark directory to track `bchains` output and `gtime -v` output per release.
- Added a load-only comparison on `chr22_graph.gfa` showing the new packed loader reduced peak RSS from about 3.12 GB to about 0.77 GB while keeping similar load time.

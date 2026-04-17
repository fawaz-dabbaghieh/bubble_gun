# 1.2.6

- Added reusable epoch-marked node and handle visitation arrays to `PackedGraph`.
- Rewrote the packed bubble search state to use those reusable arrays instead of allocating fresh Python `set`s for each search.
- Kept the packed bubble search logic otherwise unchanged to isolate the effect of the lower-overhead traversal state.
- Recorded the standard `chr22_graph.gfa` `bchains` benchmark: identical output, 50.71s wall time, and 2043520 KB max RSS.

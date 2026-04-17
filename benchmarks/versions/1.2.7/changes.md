# 1.2.7

- Replaced the packed parent-finding re-run with offline parent assignment from already-discovered bubbles.
- Built temporary superbubble containment lists by node and assigned each bubble to the smallest containing superbubble, matching the prior overwrite behavior from large to small.
- Kept the rest of packed bubble discovery unchanged so the benchmark isolates the parent-assignment strategy change.
- Recorded the standard `chr22_graph.gfa` `bchains` benchmark: identical output, 50.70s wall time, and 1769184 KB max RSS.

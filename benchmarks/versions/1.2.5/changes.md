# 1.2.5

- Switched `bchains --chains_gfa` to the packed backend when no FASTA or haplotype output is requested.
- Added packed GFA chain writing support.
- Dropped the redundant top-level `graph.bubbles` index after parent annotation, since the chains already retain the bubble objects needed for output and statistics.
- Added a regression test showing packed and legacy chain-GFA outputs match on the example graph.
- Recorded the standard `chr22_graph.gfa` `bchains` benchmark: 50.57s wall time and 1996832 KB max RSS with identical stats output.

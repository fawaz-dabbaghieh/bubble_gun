# 1.2.4

- Switched `bchains --bubble_json` to the packed integer-indexed backend when no legacy GFA/FASTA outputs are requested.
- Made JSON export work with both the legacy `Graph` objects and the packed graph objects.
- Added a semantic JSON comparison utility to compare two `bchains` JSON outputs independent of incidental chain or bubble numbering.
- Validated `benchmarks/versions/1.2.4/bchains.json` against `benchmarks/versions/1.2.0/bchains.json`; the outputs match semantically.
- Recorded the `chr22_graph.gfa` `--bubble_json` benchmark: 52.57s wall time and 2304896 KB max RSS with identical stats output.

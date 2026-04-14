# 1.2.2

- Switched the default stats-only `bchains` path to the packed integer-indexed graph backend.
- Ported bubble detection, chain connection, parent finding, and coverage/length statistics to integer node indices.
- Kept the legacy `Graph` path for `bchains` modes that still need the old sequence/GFA output code (`--bubble_json`, `--chains_gfa`, `--fasta`, `--out_haplos`).
- Added parity tests to compare packed and legacy bubble detection on the example graph.
- Recorded the first end-to-end packed benchmark on `chr22_graph.gfa`: output stayed identical, max RSS dropped to 2064864 KB from the 3579888 KB baseline, and wall time increased to 57.20s from the 51.37s baseline.

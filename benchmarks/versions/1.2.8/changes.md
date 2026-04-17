# 1.2.8

- Changed packed simple-bubble and insertion classification to use unique local neighbor topology instead of raw side-degree counts.
- This makes packed classification robust to duplicate `L` lines without adding global edge deduplication state.
- Added a regression test where duplicated `L` lines still classify a packed simple bubble correctly.
- Recorded the standard `chr22_graph.gfa` `bchains` benchmark: identical output, 52.41s wall time, and 1977168 KB max RSS.

# Benchmarks

This directory tracks BubbleGun behavior and performance by released patch
version.

## Protocol

For each version:

1. Update `BubbleGun/__version__.py`.
2. Record the code changes in `benchmarks/versions/<version>/changes.md`.
3. Run:

   ```bash
   conda run -n bubblegun python scripts/benchmark_bchains.py
   ```

4. Review:
   - `benchmarks/versions/<version>/bchains.stdout.txt`
   - `benchmarks/versions/<version>/bchains.gtime.txt`
   - `benchmarks/versions/<version>/summary.json`

The default benchmark graph is
`test/bubble_finder_graph/chr22_graph.gfa`, and the default command is:

```bash
BubbleGun -g test/bubble_finder_graph/chr22_graph.gfa bchains
```

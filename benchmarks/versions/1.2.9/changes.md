# 1.2.9

- Switched the packed bubble-finding frontier back to an unordered `set` so traversal order is closer to the `1.2.0` implementation.
- Added a per-search watchdog in `packed_bubbles.py` behind `BUBBLEGUN_DEBUG_PACKED=1` to report long-running packed searches while they are still in progress.

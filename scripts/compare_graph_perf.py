#!/usr/bin/env python3
import argparse
import gc
import time
import tracemalloc

from BubbleGun import Graph as GraphModule
from BubbleGun.find_bubbles import find_bubbles
from BubbleGun.connect_bubbles import connect_bubbles
from BubbleGun.find_parents import find_parents


def run_once(graph_cls, path, run_detection):
    gc.collect()
    tracemalloc.start()
    start = time.perf_counter()
    graph = graph_cls(path)
    load_elapsed = time.perf_counter() - start
    detect_elapsed = 0.0
    bubble_counts = (0, 0, 0)
    chain_count = 0
    if run_detection:
        start_detect = time.perf_counter()
        find_bubbles(graph, only_simple=False, only_super=False)
        connect_bubbles(graph)
        find_parents(graph)
        detect_elapsed = time.perf_counter() - start_detect
        bubble_counts = tuple(graph.bubble_number())
        chain_count = len(graph.b_chains)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    del graph
    return load_elapsed, detect_elapsed, peak, bubble_counts, chain_count


def summarize(label, results):
    load_times = [t for t, _, _, _, _ in results]
    detect_times = [t for _, t, _, _, _ in results]
    peaks = [p for _, _, p, _, _ in results]
    bubbles = [b for _, _, _, b, _ in results]
    chains = [c for _, _, _, _, c in results]
    avg_load = sum(load_times) / len(load_times)
    avg_detect = sum(detect_times) / len(detect_times)
    avg_peak = sum(peaks) / len(peaks)
    unique_bubbles = sorted(set(bubbles))
    unique_chains = sorted(set(chains))
    print(
        f"{label}: avg_load={avg_load:.4f}s avg_detect={avg_detect:.4f}s "
        f"avg_peak_python_mem={avg_peak / (1024 * 1024):.2f}MB"
    )
    print(f"{label}: bubbles={unique_bubbles} chains={unique_chains}")


def main():
    parser = argparse.ArgumentParser(
        description="Compare Python vs C++ Graph loading performance."
    )
    parser.add_argument("gfa_path", help="Path to a GFA file")
    parser.add_argument(
        "--iterations", type=int, default=3, help="Number of iterations per graph"
    )
    parser.add_argument(
        "--skip_detection",
        action="store_true",
        help="Only measure graph loading (skip bubble detection).",
    )
    args = parser.parse_args()

    py_graph_cls = getattr(GraphModule, "PythonGraph", GraphModule.Graph)
    cpp_graph_cls = GraphModule.Graph

    if py_graph_cls is cpp_graph_cls:
        print("Warning: C++ extension not available; both classes are the same.")

    print("Note: memory uses tracemalloc (Python allocations only).")

    py_results = [
        run_once(py_graph_cls, args.gfa_path, not args.skip_detection)
        for _ in range(args.iterations)
    ]
    summarize("PythonGraph", py_results)

    cpp_results = [
        run_once(cpp_graph_cls, args.gfa_path, not args.skip_detection)
        for _ in range(args.iterations)
    ]
    summarize("CppGraph", cpp_results)


if __name__ == "__main__":
    main()

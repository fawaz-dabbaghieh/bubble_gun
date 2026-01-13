#!/usr/bin/env python3
import argparse
import gc
import time
import tracemalloc

from BubbleGun import Graph as GraphModule


def run_once(graph_cls, path):
    gc.collect()
    tracemalloc.start()
    start = time.perf_counter()
    graph = graph_cls(path)
    elapsed = time.perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    del graph
    return elapsed, peak


def summarize(label, results):
    times = [t for t, _ in results]
    peaks = [p for _, p in results]
    avg_time = sum(times) / len(times)
    avg_peak = sum(peaks) / len(peaks)
    print(f"{label}: avg_time={avg_time:.4f}s avg_peak_python_mem={avg_peak / (1024 * 1024):.2f}MB")


def main():
    parser = argparse.ArgumentParser(
        description="Compare Python vs C++ Graph loading performance."
    )
    parser.add_argument("gfa_path", help="Path to a GFA file")
    parser.add_argument(
        "--iterations", type=int, default=3, help="Number of iterations per graph"
    )
    args = parser.parse_args()

    py_graph_cls = getattr(GraphModule, "PythonGraph", GraphModule.Graph)
    cpp_graph_cls = GraphModule.Graph

    if py_graph_cls is cpp_graph_cls:
        print("Warning: C++ extension not available; both classes are the same.")

    print("Note: memory uses tracemalloc (Python allocations only).")

    py_results = [run_once(py_graph_cls, args.gfa_path) for _ in range(args.iterations)]
    summarize("PythonGraph", py_results)

    cpp_results = [run_once(cpp_graph_cls, args.gfa_path) for _ in range(args.iterations)]
    summarize("CppGraph", cpp_results)


if __name__ == "__main__":
    main()

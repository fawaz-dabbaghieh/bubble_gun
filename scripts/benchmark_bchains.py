#!/usr/bin/env python3
import argparse
import json
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

from BubbleGun.__version__ import version as package_version


STAT_PATTERNS = {
    "simple_bubbles": re.compile(r"The number of Simple Bubbles is (\d+)"),
    "superbubbles": re.compile(r"The number of Superbubbles is (\d+)"),
    "insertions": re.compile(r"The number of insertions is (\d+)"),
    "sequence_coverage_pct": re.compile(r"Sequence coverage of the bubble chains is ([0-9.]+)%"),
    "node_coverage_pct": re.compile(r"Node coverage of the bubble chains is ([0-9.]+)%"),
    "longest_chain_seq_bp": re.compile(r"The longest chain seq-wise has (\d+) bp"),
    "longest_chain_bubbles": re.compile(r"The longest chain bubble_wise has (\d+) bubbles"),
    "max_rss_kb": re.compile(r"Maximum resident set size \(kbytes\): (\d+)"),
    "user_time_s": re.compile(r"User time \(seconds\): ([0-9.]+)"),
    "system_time_s": re.compile(r"System time \(seconds\): ([0-9.]+)"),
    "elapsed": re.compile(r"Elapsed \(wall clock\) time \(h:mm:ss or m:ss\): ([0-9:.]+)"),
}


def parse_metrics(stdout_text, gtime_text):
    metrics = {}
    for key, pattern in STAT_PATTERNS.items():
        text = gtime_text if key in {"max_rss_kb", "user_time_s", "system_time_s", "elapsed"} else stdout_text
        match = pattern.search(text)
        if match:
            value = match.group(1)
            if key == "elapsed":
                metrics[key] = value
            elif "." in value:
                metrics[key] = float(value)
            else:
                metrics[key] = int(value)
    return metrics


def git_commit(repo_root):
    try:
        return (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=repo_root,
                text=True,
            )
            .strip()
        )
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser(description="Run and record a BubbleGun bchains benchmark.")
    parser.add_argument(
        "--graph",
        default="test/bubble_finder_graph/chr22_graph.gfa",
        help="Graph path relative to repo root or absolute path",
    )
    parser.add_argument(
        "--version",
        default=package_version,
        help="Version directory to write benchmark artifacts to",
    )
    parser.add_argument(
        "--output-root",
        default="benchmarks/versions",
        help="Root directory for versioned benchmark outputs",
    )
    parser.add_argument(
        "--executable",
        default="BubbleGun",
        help="BubbleGun executable to run",
    )
    parser.add_argument(
        "--gtime",
        default="gtime",
        help="GNU time executable",
    )
    parser.add_argument(
        "extra_args",
        nargs=argparse.REMAINDER,
        help="Extra arguments passed to the BubbleGun bchains command",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    graph_path = Path(args.graph)
    if not graph_path.is_absolute():
        graph_path = repo_root / graph_path
    graph_path = graph_path.resolve()

    if not graph_path.exists():
        raise SystemExit("graph file does not exist: {}".format(graph_path))
    if shutil.which(args.executable) is None:
        raise SystemExit("BubbleGun executable not found: {}".format(args.executable))
    if shutil.which(args.gtime) is None:
        raise SystemExit("GNU time executable not found: {}".format(args.gtime))

    version_dir = repo_root / args.output_root / args.version
    version_dir.mkdir(parents=True, exist_ok=True)

    stdout_path = version_dir / "bchains.stdout.txt"
    gtime_path = version_dir / "bchains.gtime.txt"
    metadata_path = version_dir / "metadata.json"
    summary_path = version_dir / "summary.json"

    command = [
        args.gtime,
        "-v",
        args.executable,
        "-g",
        str(graph_path),
        "bchains",
    ]
    if args.extra_args and args.extra_args[0] == "--":
        command.extend(args.extra_args[1:])
    else:
        command.extend(args.extra_args)

    completed = subprocess.run(
        command,
        cwd=repo_root,
        text=True,
        capture_output=True,
    )

    stdout_path.write_text(completed.stdout)
    gtime_path.write_text(completed.stderr)

    metadata = {
        "version": args.version,
        "package_version": package_version,
        "command": command,
        "graph": str(graph_path),
        "exit_code": completed.returncode,
        "python": sys.version,
        "platform": platform.platform(),
        "git_commit": git_commit(repo_root),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True))

    summary = parse_metrics(completed.stdout, completed.stderr)
    summary["exit_code"] = completed.returncode
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True))

    print("Wrote benchmark artifacts to {}".format(version_dir))
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


if __name__ == "__main__":
    main()

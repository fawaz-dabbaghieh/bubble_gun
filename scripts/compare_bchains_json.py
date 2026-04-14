#!/usr/bin/env python3
import argparse
import sys

from BubbleGun.json_compare import compare_bchains_json


def main():
    parser = argparse.ArgumentParser(description="Compare two BubbleGun bchains JSON outputs semantically.")
    parser.add_argument("first_json", help="First JSON output")
    parser.add_argument("second_json", help="Second JSON output")
    args = parser.parse_args()

    matches, first_normalized, second_normalized = compare_bchains_json(
        args.first_json,
        args.second_json,
    )

    if matches:
        print("JSON outputs match semantically.")
        return 0

    print("JSON outputs differ.")
    print("First normalized chains:", len(first_normalized))
    print("Second normalized chains:", len(second_normalized))
    return 1


if __name__ == "__main__":
    sys.exit(main())

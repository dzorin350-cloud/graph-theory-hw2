"""Run both planarity algorithms on one or more graph files.

Usage:
    python3 main.py                  # every file in samples/
    python3 main.py my_graph.txt     # specific files
"""

import argparse
import sys
import time
from pathlib import Path

from bm_planarity import boyer_myrvold_is_planar
from graph_io import count_edges, load_graph
from ht_planarity import hopcroft_tarjan_is_planar


def algorithms():
    """Return the (name, function) pairs of the implemented tests."""
    return (("Hopcroft-Tarjan", hopcroft_tarjan_is_planar),
            ("Boyer-Myrvold", boyer_myrvold_is_planar))


def run_algorithm(name, test, adjacency):
    """Time one planarity test, print its verdict and return it."""
    start = time.perf_counter()
    planar = test(adjacency)
    elapsed_ms = (time.perf_counter() - start) * 1000
    verdict = "PLANAR" if planar else "NOT PLANAR"
    print(f"  {name:<16} {verdict:<11} {elapsed_ms:9.3f} ms")
    return planar


def report_file(path):
    """Load a graph file and print the result of both algorithms."""
    adjacency = load_graph(path)
    print(f"{Path(path).name}  |V| = {len(adjacency)}  "
          f"|E| = {count_edges(adjacency)}")
    verdicts = {run_algorithm(name, test, adjacency)
                for name, test in algorithms()}
    if len(verdicts) > 1:
        print("  WARNING: the two algorithms disagree")
    print()


def main():
    """Parse the command line and report every requested graph file."""
    parser = argparse.ArgumentParser(description="Graph planarity tests")
    parser.add_argument("files", nargs="*", help="edge-list graph files")
    arguments = parser.parse_args()
    sample_dir = Path(__file__).resolve().parent / "samples"
    files = arguments.files or sorted(sample_dir.glob("*.txt"))
    sys.setrecursionlimit(100000)
    for path in files:
        report_file(path)


if __name__ == "__main__":
    main()

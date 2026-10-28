"""Graph loading and small helpers shared by both planarity algorithms.

A graph is stored as an adjacency dict: vertex label -> set of neighbours.
Input files contain one edge per line ("u v"); a line with a single label
declares an isolated vertex; blank lines and lines starting with '#' are
ignored.  Self-loops and parallel edges never change planarity, so they
are dropped while loading.
"""


def add_edge(adjacency, first, second):
    """Insert the undirected edge first-second, ignoring self-loops."""
    adjacency.setdefault(first, set())
    adjacency.setdefault(second, set())
    if first != second:
        adjacency[first].add(second)
        adjacency[second].add(first)


def load_graph(path):
    """Read a graph file and return its adjacency dict."""
    adjacency = {}
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            tokens = line.split("#", 1)[0].split()
            if len(tokens) == 1:
                adjacency.setdefault(tokens[0], set())
            elif len(tokens) >= 2:
                add_edge(adjacency, tokens[0], tokens[1])
    return adjacency


def adjacency_from_edges(edges):
    """Build an adjacency dict from an iterable of (u, v) pairs."""
    adjacency = {}
    for first, second in edges:
        add_edge(adjacency, first, second)
    return adjacency


def count_edges(adjacency):
    """Return the number of undirected edges of the graph."""
    return sum(len(neighbours) for neighbours in adjacency.values()) // 2


def exceeds_euler_bound(adjacency):
    """Return True if |E| > 3|V| - 6, which proves non-planarity.

    Euler's formula gives |E| <= 3|V| - 6 for every simple planar graph
    with at least 3 vertices, so this is a cheap early rejection.
    """
    vertex_count = len(adjacency)
    return vertex_count > 2 and count_edges(adjacency) > 3 * vertex_count - 6

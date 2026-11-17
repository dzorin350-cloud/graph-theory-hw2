"""Maximum flow with Dinic's algorithm (level graph + blocking flow).

Usage: python dinic.py network.txt [--steps]
"""

import sys
from collections import deque

from flow_network import load_from_args, print_result


def bfs_levels(network):
    """Give each node its BFS distance from the source in the residual graph."""
    level = [-1] * network.n
    level[network.source] = 0
    queue = deque([network.source])
    while queue:
        u = queue.popleft()
        for v, residual, _ in network.graph[u]:
            if residual > 0 and level[v] == -1:
                level[v] = level[u] + 1
                queue.append(v)
    return level


def dfs_augment(network, u, pushed, level, next_edge, path):
    """Send flow from u to the sink using only edges going one level deeper."""
    if u == network.sink:
        return pushed
    while next_edge[u] < len(network.graph[u]):
        edge = network.graph[u][next_edge[u]]
        v, residual, _ = edge
        if residual > 0 and level[v] == level[u] + 1:
            path.append(v)
            sent = dfs_augment(network, v, min(pushed, residual), level, next_edge, path)
            if sent > 0:
                network.push(u, edge, sent)
                return sent
            path.pop()
        next_edge[u] += 1          # this edge is useless for the rest of the phase
    return 0


def dinic(network, show_steps=False):
    total = 0
    phase = 0
    while True:
        level = bfs_levels(network)
        if level[network.sink] == -1:
            break                  # sink unreachable: no augmenting path left
        phase += 1
        if show_steps:
            layers = {}
            for i, d in enumerate(level):
                if d >= 0:
                    layers.setdefault(d, []).append(network.names[i])
            print("\nPhase {} - level graph:".format(phase))
            for d in sorted(layers):
                print("  level {}: {}".format(d, ", ".join(layers[d])))

        next_edge = [0] * network.n
        while True:
            path = [network.source]
            sent = dfs_augment(network, network.source, float("inf"), level, next_edge, path)
            if sent == 0:
                break              # blocking flow reached for this level graph
            total += sent
            if show_steps:
                route = "-".join(network.names[i] for i in path)
                print("  augment {} along {} (total = {})".format(sent, route, total))
    return total


def main():
    loaded = load_from_args(sys.argv[1:], "Usage: python dinic.py network.txt [--steps]")
    if loaded is None:
        return
    network, show_steps = loaded
    max_flow = dinic(network, show_steps)
    print_result(network, max_flow, "Dinic's algorithm")


if __name__ == "__main__":
    main()

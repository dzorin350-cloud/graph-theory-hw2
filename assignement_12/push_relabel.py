"""Maximum flow with the Push-Relabel algorithm (Goldberg-Tarjan, FIFO order).

Usage: python push_relabel.py network.txt [--steps]
"""

import sys
from collections import deque

from flow_network import load_from_args, print_result


def push_relabel(network, show_steps=False):
    n, s, t = network.n, network.source, network.sink
    height = [0] * n
    excess = [0] * n
    names = network.names

    # Preflow: the source starts at height n and saturates all its outgoing edges.
    height[s] = n
    active = deque()
    for edge in network.graph[s]:
        v, residual, _ = edge
        if residual > 0:
            network.push(s, edge, residual)
            excess[v] += residual
            excess[s] -= residual
            if v != t and excess[v] == residual:
                active.append(v)
            if show_steps:
                print("init: push {} from {} to {}".format(residual, names[s], names[v]))

    while active:
        u = active.popleft()
        # Discharge u: push its excess away, relabel when no admissible edge exists.
        while excess[u] > 0:
            pushed_any = False
            for edge in network.graph[u]:
                v, residual, _ = edge
                if residual > 0 and height[u] == height[v] + 1:
                    amount = min(excess[u], residual)
                    network.push(u, edge, amount)
                    excess[u] -= amount
                    excess[v] += amount
                    if show_steps:
                        print("push {} from {} to {}".format(amount, names[u], names[v]))
                    if v != s and v != t and excess[v] == amount:
                        active.append(v)   # v just became active
                    pushed_any = True
                    if excess[u] == 0:
                        break
            if excess[u] > 0 and not pushed_any:
                new_height = 1 + min(height[v] for v, residual, _ in network.graph[u]
                                     if residual > 0)
                if show_steps:
                    print("relabel {}: height {} -> {}".format(names[u], height[u], new_height))
                height[u] = new_height

    return excess[t]


def main():
    loaded = load_from_args(sys.argv[1:], "Usage: python push_relabel.py network.txt [--steps]")
    if loaded is None:
        return
    network, show_steps = loaded
    max_flow = push_relabel(network, show_steps)
    print_result(network, max_flow, "Push-Relabel algorithm")


if __name__ == "__main__":
    main()

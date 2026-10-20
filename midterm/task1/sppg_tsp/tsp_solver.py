"""Exact asymmetric TSP solver (depot = vertex 0), using Branch & Bound.

No mapping or third-party dependencies.

The input is a directed distance matrix: D[i][j] is the cost of travelling
from stop i to stop j, and may differ from D[j][i]. ``math.inf`` means the
arc is unavailable. Costs must be non-negative.

The branch-and-bound lower bound combines:
  * minimum missing outgoing-edge costs;
  * minimum missing incoming-edge costs;
  * directed cut-set bounds on subsets of the still-unvisited schools.

All lower bounds are *admissible*: they never exceed the cost of a complete
feasible tour extending the current partial tour. Thus pruning preserves
optimality, provided the search finishes before the optional deadline.

Usage:
    from tsp_solver import solve_tsp
    D = [[0, 4, 2], [3, 0, 6], [7, 1, 0]]
    print(solve_tsp(D))

An unreachable instance yields route=[] and distance=math.inf. If the
search has completed, optimal=True also certifies that no tour exists.
If a deadline expires, optimal=False (even if a feasible tour was found).
"""

from __future__ import annotations

import math
import time
from collections.abc import Sequence


def _validate_matrix(D: Sequence[Sequence[float]]) -> list[list[float]]:
    try:
        size = len(D)
    except TypeError as exc:
        raise ValueError("D must be a nonempty square matrix") from exc
    if size == 0:
        raise ValueError("D must contain at least the depot (vertex 0)")

    matrix: list[list[float]] = []
    for i, row in enumerate(D):
        if len(row) != size:
            raise ValueError(f"Row {i} has length {len(row)}; expected {size}")
        validated_row = []
        for j, raw_value in enumerate(row):
            try:
                value = float(raw_value)
            except (TypeError, ValueError, OverflowError) as exc:
                raise ValueError(f"D[{i}][{j}] must be a nonnegative number or +inf") from exc
            if math.isnan(value) or value < 0 or value == -math.inf:
                raise ValueError(f"D[{i}][{j}] must be nonnegative (or +inf)")
            validated_row.append(value)
        matrix.append(validated_row)
    return matrix


def _cluster_masks(clusters: list[list[int]] | None, size: int) -> tuple[int, ...]:
    if clusters is None:
        return ()
    masks: set[int] = set()
    for group in clusters:
        mask = 0
        for vertex in group:
            if isinstance(vertex, bool) or not isinstance(vertex, int) or not (1 <= vertex < size):
                raise ValueError("Cluster indices must be school vertices in 1..n-1")
            mask |= 1 << vertex
        if mask:
            masks.add(mask)
    return tuple(sorted(masks))


def solve_tsp(
    D: list[list[float]],
    timeout_s: float = 30.0,
    clusters: list[list[int]] | None = None,
) -> dict:
    """Solve an asymmetric TSP using exact branch-and-bound search.

    Args:
        D: Square nonnegative distance matrix, in any consistent cost unit.
           Vertex 0 is the depot. Off-diagonal +inf denotes a forbidden arc.
        timeout_s: Maximum approximate search time in seconds; ``math.inf``
           disables the deadline. 0 returns the greedy incumbent if any,
           without an optimality claim (except trivial instances).
        clusters: Optional groups of school indices (1..n-1). Their
           intersections with the unvisited set contribute additional
           directed cut-set lower bounds. Not required for correctness.

    Returns:
        dict with ``route``, ``distance``, ``elapsed_s``, ``optimal``,
        ``explored_nodes``, ``pruned_nodes``. A route includes vertex 0 at
        both ends, e.g. [0, 2, 1, 0]. No feasible route is represented by
        [] and math.inf. ``optimal`` only means the best cost (or infeasibility)
        has been *proved*, not merely that an incumbent was found.

    Complexity:
        Exponential/factorial in the worst case. The degree and cut bounds,
        dominance cache, and greedy incumbent often prune many branches.
        The returned elapsed_s includes preprocessing and the initial greedy
        tour, but not any external road-network computation.
    """
    start = time.perf_counter()
    dist = _validate_matrix(D)
    n = len(dist)
    try:
        timeout = float(timeout_s)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("timeout_s must be nonnegative") from exc
    if math.isnan(timeout) or timeout < 0:
        raise ValueError("timeout_s must be nonnegative")
    groups = _cluster_masks(clusters, n)

    def result(route: list[int], distance: float, optimal: bool,
               explored: int, pruned: int) -> dict:
        return {
            "route": route,
            "distance": distance,
            "elapsed_s": time.perf_counter() - start,
            "optimal": optimal,
            "explored_nodes": explored,
            "pruned_nodes": pruned,
        }

    # Only the depot: no journey is necessary, regardless of D[0][0].
    if n == 1:
        return result([0, 0], 0.0, True, 1, 0)

    # Exactly one school: there is precisely one possible visit order.
    if n == 2:
        cost = dist[0][1] + dist[1][0]
        return result([0, 1, 0] if math.isfinite(cost) else [], cost,
                      True, 1, 0)

    schools_mask = ((1 << n) - 1) ^ 1
    deadline = start + timeout if math.isfinite(timeout) else math.inf

    # Nearest-neighbor upper bound. It is merely a feasible *incumbent*;
    # failure does not imply that the directed TSP is infeasible.
    greedy_route = [0]
    current = 0
    unvisited = set(range(1, n))
    greedy_cost = 0.0
    while unvisited:
        next_stop = min(unvisited, key=lambda v: (dist[current][v], v))
        arc_cost = dist[current][next_stop]
        if not math.isfinite(arc_cost):
            break
        greedy_cost += arc_cost
        greedy_route.append(next_stop)
        unvisited.remove(next_stop)
        current = next_stop

    if not unvisited and math.isfinite(dist[current][0]):
        greedy_cost += dist[current][0]
        best_cost = greedy_cost
        best_route = greedy_route + [0]
    else:
        best_cost = math.inf
        best_route = []

    # Every valid TSP cost is >= 0 by validation.
    if best_cost == 0:
        return result(best_route, 0.0, True, 0, 0)

    explored_nodes = 0
    pruned_nodes = 0
    # Dominance: future possibilities depend only on (visited set, last).
    # A more expensive prefix to the same state can never be better.
    min_prefix_cost: dict[tuple[int, int], float] = {}

    def lower_bound(last: int, remaining_mask: int, prefix_cost: float) -> float:
        """Admissible bound for finishing a directed path at ``last``.

        Missing edges must leave {last} U remaining and arrive at
        remaining U {depot}. No early last->depot edge is allowed while any
        schools remain. This is a relaxation, not an assignment solver.
        """
        if remaining_mask == 0:
            return prefix_cost + dist[last][0]

        remaining = [v for v in range(1, n) if remaining_mask & (1 << v)]

        # One missing outgoing edge from last and from each unvisited school.
        outgoing_cost = prefix_cost
        for source in [last, *remaining]:
            targets = remaining if source == last else [*remaining, 0]
            edge = min((dist[source][target] for target in targets
                        if target != source), default=math.inf)
            outgoing_cost += edge
            if not math.isfinite(outgoing_cost):
                return math.inf

        # One missing incoming edge for each unvisited school and the depot.
        incoming_cost = prefix_cost
        for target in [*remaining, 0]:
            sources = remaining if target == 0 else [last, *remaining]
            edge = min((dist[source][target] for source in sources
                        if source != target), default=math.inf)
            incoming_cost += edge
            if not math.isfinite(incoming_cost):
                return math.inf

        bound = max(outgoing_cost, incoming_cost)

        # Directed cut sets. For Z subset of unvisited schools, a completion
        # needs an incoming edge from {last} U (remaining\Z) to Z AND an
        # outgoing edge from Z to {depot} U (remaining\Z). Both edges are
        # missing from the prefix and hence can be added to its cost.
        cuts = {remaining_mask}
        cuts.update(mask & remaining_mask for mask in groups)
        for subset in cuts:
            if subset == 0:
                continue
            inside = [v for v in remaining if subset & (1 << v)]
            outside = [v for v in remaining if not subset & (1 << v)]
            entering = min(
                (dist[source][target]
                 for source in [last, *outside] for target in inside),
                default=math.inf,
            )
            leaving = min(
                (dist[source][target]
                 for source in inside for target in [*outside, 0]),
                default=math.inf,
            )
            bound = max(bound, prefix_cost + entering + leaving)
            if not math.isfinite(bound):
                return math.inf
        return bound

    # Iterative depth-first search avoids Python recursion limits. Pushing
    # successors in reversed greedy order explores shorter arcs first.
    stack: list[tuple[int, int, float, tuple[int, ...]]] = [
        (1, 0, 0.0, (0,))
    ]
    while stack:
        if time.perf_counter() >= deadline:
            return result(best_route, best_cost, False,
                          explored_nodes, pruned_nodes)

        visited_mask, last, prefix_cost, path = stack.pop()
        explored_nodes += 1

        if prefix_cost >= best_cost:
            pruned_nodes += 1
            continue

        key = (last, visited_mask)
        prev = min_prefix_cost.get(key, math.inf)
        if prefix_cost >= prev:
            pruned_nodes += 1
            continue
        min_prefix_cost[key] = prefix_cost

        remaining_mask = schools_mask & ~visited_mask
        if remaining_mask == 0:
            total = prefix_cost + dist[last][0]
            if total < best_cost:
                best_cost = total
                best_route = [*path, 0]
            continue

        if lower_bound(last, remaining_mask, prefix_cost) >= best_cost:
            pruned_nodes += 1
            continue

        successors = sorted(
            (v for v in range(1, n)
             if (remaining_mask & (1 << v)) and math.isfinite(dist[last][v])),
            key=lambda v: (dist[last][v], v),
        )
        for next_stop in reversed(successors):
            new_cost = prefix_cost + dist[last][next_stop]
            if new_cost < best_cost:
                stack.append((visited_mask | (1 << next_stop), next_stop,
                              new_cost, (*path, next_stop)))
            else:
                pruned_nodes += 1

    return result(best_route, best_cost, True,
                  explored_nodes, pruned_nodes)


if __name__ == "__main__":
    example = [[0, 4, 2], [3, 0, 6], [7, 1, 0]]
    print(solve_tsp(example))

"""Exact Held-Karp dynamic programming solver for the asymmetric TSP."""

from __future__ import annotations

import math
import time
from collections.abc import Sequence


def _validate_matrix(D: Sequence[Sequence[float]]) -> list[list[float]]:
    """Validate D and return a numeric square copy."""
    try:
        size = len(D)
    except TypeError as error:
        raise ValueError("D doit être une matrice carrée non vide") from error
    if size == 0:
        raise ValueError("D doit contenir au moins le SPPG (sommet 0)")

    matrix: list[list[float]] = []
    for row_index, row in enumerate(D):
        if len(row) != size:
            raise ValueError(
                f"La ligne {row_index} contient {len(row)} valeurs; "
                f"{size} attendues"
            )
        numeric_row: list[float] = []
        for column_index, value in enumerate(row):
            try:
                number = float(value)
            except (TypeError, ValueError, OverflowError) as error:
                raise ValueError(
                    f"D[{row_index}][{column_index}] doit être un nombre ou +inf"
                ) from error
            if math.isnan(number) or number < 0:
                raise ValueError(
                    f"D[{row_index}][{column_index}] doit être positif ou +inf"
                )
            numeric_row.append(number)
        matrix.append(numeric_row)
    return matrix


def solve_tsp(D: Sequence[Sequence[float]]) -> dict[str, object]:
    """Return an optimal directed TSP tour using Held-Karp dynamic programming.

    Vertex 0 is the SPPG.  A ``ValueError`` is raised when no complete tour
    exists; no school is removed from the problem.
    """
    started_at = time.perf_counter()
    matrix = _validate_matrix(D)
    size = len(matrix)

    if size == 1:
        return {
            "route": [0, 0],
            "distance": 0.0,
            "elapsed_s": time.perf_counter() - started_at,
            "optimal": True,
        }

    # dp[(mask, last)] is the cheapest path 0 -> ... -> last.
    # Bit vertex-1 represents school vertex `vertex`.
    dp: dict[tuple[int, int], float] = {}
    parent: dict[tuple[int, int], int | None] = {}

    for school in range(1, size):
        cost = matrix[0][school]
        if math.isfinite(cost):
            mask = 1 << (school - 1)
            dp[(mask, school)] = cost
            parent[(mask, school)] = None

    school_count = size - 1
    for subset_size in range(2, school_count + 1):
        for mask in range(1 << school_count):
            if mask.bit_count() != subset_size:
                continue
            for last in range(1, size):
                last_bit = 1 << (last - 1)
                if not mask & last_bit:
                    continue

                previous_mask = mask ^ last_bit
                best_cost = math.inf
                best_previous: int | None = None
                for previous in range(1, size):
                    previous_bit = 1 << (previous - 1)
                    if not previous_mask & previous_bit:
                        continue
                    previous_cost = dp.get((previous_mask, previous), math.inf)
                    edge_cost = matrix[previous][last]
                    candidate = previous_cost + edge_cost
                    if candidate < best_cost:
                        best_cost = candidate
                        best_previous = previous

                if best_previous is not None:
                    dp[(mask, last)] = best_cost
                    parent[(mask, last)] = best_previous

    complete_mask = (1 << school_count) - 1
    best_distance = math.inf
    last_school: int | None = None
    for last in range(1, size):
        path_cost = dp.get((complete_mask, last), math.inf)
        candidate = path_cost + matrix[last][0]
        if candidate < best_distance:
            best_distance = candidate
            last_school = last

    if last_school is None or not math.isfinite(best_distance):
        raise ValueError("Aucune tournée complète n'est possible")

    # Follow parent pointers backwards, then reverse the school order.
    reversed_schools: list[int] = []
    mask = complete_mask
    current = last_school
    while current is not None:
        reversed_schools.append(current)
        previous = parent[(mask, current)]
        mask ^= 1 << (current - 1)
        current = previous
    route = [0, *reversed(reversed_schools), 0]

    # Recalculate from the original directed matrix after reconstruction.
    distance = sum(matrix[source][target] for source, target in zip(route, route[1:]))
    return {
        "route": route,
        "distance": distance,
        "elapsed_s": time.perf_counter() - started_at,
        "optimal": True,
    }


if __name__ == "__main__":
    example_matrix = [
        [0, 4, 2, 7],
        [3, 0, 6, 1],
        [8, 5, 0, 3],
        [2, 4, 6, 0],
    ]
    print(solve_tsp(example_matrix))

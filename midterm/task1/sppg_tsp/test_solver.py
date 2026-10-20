"""Correctness checks for tsp_solver.py (no nonstandard dependencies).

Run with:
    python -m unittest -v test_solver.py

The exhaustive oracle enumerates every school ordering for small directed
matrices and is independent of the Branch & Bound logic.
"""

import itertools
import math
import random
import unittest

from tsp_solver import solve_tsp


def brute_force_tsp(D):
    """Enumerate ALL tours; only practical for small problem instances."""
    n = len(D)
    if n == 1:
        return [0, 0], 0.0

    minimum = math.inf
    best_route = []
    for schools in itertools.permutations(range(1, n)):
        candidate = (0, *schools, 0)
        total = sum(D[a][b] for a, b in zip(candidate, candidate[1:]))
        if total < minimum:
            minimum = total
            best_route = list(candidate)
    return best_route, minimum


def check_solution(testcase, D, answer, optimal=True):
    testcase.assertEqual(
        set(answer),
        {"route", "distance", "elapsed_s", "optimal", "explored_nodes", "pruned_nodes"},
    )
    testcase.assertIsInstance(answer["optimal"], bool)
    testcase.assertGreaterEqual(answer["elapsed_s"], 0)
    testcase.assertGreaterEqual(answer["explored_nodes"], 0)
    testcase.assertGreaterEqual(answer["pruned_nodes"], 0)
    if optimal:
        testcase.assertTrue(answer["optimal"])

    route = answer["route"]
    if not route:
        testcase.assertEqual(answer["distance"], math.inf)
    else:
        testcase.assertEqual(route[0], 0)
        testcase.assertEqual(route[-1], 0)
        testcase.assertEqual(len(route), len(D) + 1)
        testcase.assertEqual(sorted(route[1:-1]), list(range(1, len(D))))
        actual = (0.0 if len(D) == 1 else
                  sum(D[a][b] for a, b in zip(route, route[1:])))
        testcase.assertTrue(math.isfinite(actual))
        testcase.assertAlmostEqual(actual, answer["distance"])


class TestAsymmetricTSP(unittest.TestCase):
    def test_zero_schools(self):
        result = solve_tsp([[math.inf]])
        check_solution(self, [[math.inf]], result)
        self.assertEqual(result["route"], [0, 0])
        self.assertEqual(result["distance"], 0)

    def test_one_school(self):
        D = [[0, 4], [8, 0]]
        result = solve_tsp(D)
        check_solution(self, D, result)
        self.assertEqual(result["route"], [0, 1, 0])
        self.assertEqual(result["distance"], 12)

    def test_one_school_unreachable(self):
        D = [[0, math.inf], [2, 0]]
        result = solve_tsp(D)
        check_solution(self, D, result)
        self.assertEqual(result["route"], [])
        self.assertEqual(result["distance"], math.inf)
        self.assertTrue(result["optimal"])

    def test_asymmetric_known_optimum(self):
        D = [[0, 4, 2], [3, 0, 6], [7, 1, 0]]
        result = solve_tsp(D)
        check_solution(self, D, result)
        self.assertEqual(result["route"], [0, 2, 1, 0])
        self.assertEqual(result["distance"], 6)

    def test_greedy_trap_but_feasible(self):
        I = math.inf
        # Nearest-neighbor picks 0->1 and gets stuck. 0->2->1->0 works.
        D = [[0, 1, 2], [1, 0, I], [1, 1, 0]]
        result = solve_tsp(D)
        check_solution(self, D, result)
        self.assertEqual(result["route"], [0, 2, 1, 0])
        self.assertEqual(result["distance"], 4)

    def test_infeasible_three_schools(self):
        I = math.inf
        D = [[0, 1, I, I], [1, 0, I, I], [I, I, 0, 1], [I, I, 1, 0]]
        result = solve_tsp(D)
        check_solution(self, D, result)
        self.assertEqual(result["route"], [])
        self.assertEqual(result["distance"], math.inf)

    def test_zero_costs_and_ties(self):
        D = [[0, 0, 0, 0] for _ in range(4)]
        result = solve_tsp(D)
        check_solution(self, D, result)
        self.assertEqual(result["distance"], 0)
        self.assertTrue(result["optimal"])

    def test_equal_costs(self):
        D = [[0 if i == j else 1 for j in range(6)] for i in range(6)]
        result = solve_tsp(D)
        check_solution(self, D, result)
        self.assertEqual(result["distance"], 6)

    def test_timeout_zero_returns_unproved_greedy(self):
        D = [[0 if i == j else abs(i - j) + 1 for j in range(6)] for i in range(6)]
        result = solve_tsp(D, timeout_s=0)
        check_solution(self, D, result, optimal=False)
        self.assertFalse(result["optimal"])
        self.assertEqual(result["explored_nodes"], 0)
        self.assertTrue(math.isfinite(result["distance"]))

    def test_timeout_zero_without_incumbent(self):
        I = math.inf
        D = [[0, 1, 2], [1, 0, I], [1, 1, 0]]
        result = solve_tsp(D, timeout_s=0)
        check_solution(self, D, result, optimal=False)
        self.assertFalse(result["optimal"])
        self.assertEqual(result["route"], [])
        self.assertEqual(result["distance"], math.inf)

    def test_fractional_weights_against_exhaustive_oracle(self):
        randomizer = random.Random(581)
        for trial in range(25):
            n = 9
            D = [[
                0 if i == j else (
                    math.inf if randomizer.random() < 0.08
                    else randomizer.randint(1, 30) / 10
                ) for j in range(n)
            ] for i in range(n)]
            _, oracle = brute_force_tsp(D)
            result = solve_tsp(
                D, timeout_s=math.inf,
                clusters=[list(range(1, 4)), list(range(4, 7))],
            )
            with self.subTest(trial=trial):
                check_solution(self, D, result)
                if math.isinf(oracle):
                    self.assertEqual(result["distance"], math.inf)
                else:
                    # Floating-point sums of the same arcs may differ by
                    # a few ulps depending on their evaluation order.
                    self.assertTrue(math.isclose(
                        result["distance"], oracle, abs_tol=1e-9
                    ))

    def test_positive_timeout_reports_unproved_solution(self):
        randomizer = random.Random(581)
        n = 13
        D = [[0 if i == j else randomizer.randint(1, 200)
              for j in range(n)] for i in range(n)]
        result = solve_tsp(D, timeout_s=1e-12)
        check_solution(self, D, result, optimal=False)
        self.assertFalse(result["optimal"])
        self.assertTrue(math.isfinite(result["distance"]))

    def test_invalid_matrices(self):
        bad_inputs = [[], [[0, 1], [2]], [[0, -2], [3, 0]],
                      [[0, math.nan], [1, 0]], [[0, -math.inf], [2, 0]],
                      [[0, "bad"], [3, 0]]]
        for D in bad_inputs:
            with self.subTest(matrix=D), self.assertRaises(ValueError):
                solve_tsp(D)

    def test_invalid_timeout(self):
        for timeout in [-1, math.nan, "bad"]:
            with self.subTest(timeout=timeout), self.assertRaises(ValueError):
                solve_tsp([[0]], timeout_s=timeout)

    def test_invalid_clusters(self):
        D = [[0, 1, 2], [2, 0, 1], [1, 2, 0]]
        for clusters in [[[0]], [[-1]], [[3]], [[1.5]], [[True]]]:
            with self.subTest(clusters=clusters), self.assertRaises(ValueError):
                solve_tsp(D, clusters=clusters)

    def test_random_matrices_against_exhaustive_oracle(self):
        randomizer = random.Random(20261020)
        # Directed costs are independent; 20% of the arcs may be forbidden.
        for n in range(1, 9):
            for trial in range(30 if n <= 7 else 8):
                D = [[
                    0 if i == j else (
                        math.inf if randomizer.random() < 0.20
                        else randomizer.randint(0, 30)
                    )
                    for j in range(n)
                ] for i in range(n)]
                reference_route, reference_cost = brute_force_tsp(D)
                # Overlapping and empty clusters exercise cut-set handling.
                groups = [
                    [j for j in range(1, n) if randomizer.random() < 0.55],
                    [j for j in range(1, n) if randomizer.random() < 0.45],
                ]
                for clusters in (None, groups):
                    with self.subTest(n=n, trial=trial, clusters=clusters):
                        result = solve_tsp(D, timeout_s=math.inf, clusters=clusters)
                        check_solution(self, D, result)
                        self.assertEqual(result["distance"], reference_cost)
                        if math.isinf(reference_cost):
                            self.assertEqual(result["route"], [])
                        else:
                            self.assertEqual(len(reference_route), len(result["route"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)

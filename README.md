# Graph Theory HW2 — Minimum Spanning Tree

Informatics ITS Graph Theory class — Group ___ (fill in group number/members)

## Algorithm: Borůvka's Algorithm (task 3 — independent algorithm)

Borůvka's algorithm finds a Minimum Spanning Tree by growing many components
in parallel, instead of growing a single tree (Prim's) or globally sorting
all edges (Kruskal's):

1. Start with every vertex as its own separate component.
2. While more than one component remains:
   - Each component finds its own cheapest edge leading to a *different*
     component.
   - All such edges are added at once (skipping any that would connect two
     vertices already in the same component, which would create a cycle).
3. Repeat until only one component is left — the collected edges form the MST.

Union-Find (`find` / `union`) is used to track which component each vertex
currently belongs to and to detect/avoid cycles in O(~1) per check.

## Prerequisites

- Python 3.8+ (no external libraries required — standard library only)

## How to run

```bash
python3 boruvka_mst.py
```

The graph and edge weights used for the sample run are defined directly in
the `if __name__ == "__main__":` block at the bottom of `boruvka_mst.py`.

## Sample run result

Graph: vertices A–G, edges as listed in `boruvka_mst.py`.

```
Round 1: added [('A', 'G', 5), ('C', 'B', 5), ('E', 'D', 5), ('F', 'E', 5)], components left = 3
Round 2: added [('A', 'C', 6), ('G', 'F', 6)], components left = 1

MST edges: [('A', 'G', 5), ('C', 'B', 5), ('E', 'D', 5), ('F', 'E', 5), ('A', 'C', 6), ('G', 'F', 6)]
Total MST weight: 32
```

This matches the MST weight found independently via Kruskal's algorithm on
the same graph (32), confirming correctness.

## AI tools usage disclosure

Claude (Anthropic) was used to select and explain Borůvka's algorithm as the
"independent" third algorithm, and to help write and debug the
`boruvka_mst.py` implementation above.

## Status

- [x] Task 3 — independent algorithm (Borůvka's) — this file
- [ ] Task 1 — Prim's algorithm
- [ ] Task 2 — Kruskal's algorithm
- [ ] Task 4 — failure simulation (node/edge removal) + PDF report

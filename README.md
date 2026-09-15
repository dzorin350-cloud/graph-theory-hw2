# Graph Theory HW2 — Minimum Spanning Tree

**Informatics ITS Graph Theory class — Group 5**

This repository contains the complete implementation of three Minimum Spanning Tree (MST) algorithms and a network failure simulation, applied to a 7-node weighted graph.

## Algorithms Implemented

1. **Prim's Algorithm (Task 1):** Grows a single tree from a starting vertex by greedily selecting the cheapest connected edge.
2. **Kruskal's Algorithm (Task 2):** Globally sorts all edges and adds them one by one, utilizing a Union-Find data structure to prevent cycles.
3. **Borůvka's Algorithm (Task 3 — Independent Algorithm):** Finds an MST by growing many components in parallel. 
4. **Edge Failure Simulation (Task 4):** Simulates the removal of a critical edge to demonstrate how the network recalculates the optimal spanning tree.

## Prerequisites

* Python 3.8+ (no external libraries required — standard library only)

## How to run

```bash
python3 mst_algorithms.py
```

## Sample Run Results

* **Graph:** Vertices A–G, 12 total edges.
* **Standard MST:** All three algorithms calculate the identical optimal MST with a total weight of **32**.
* **Failure Simulation:** After removing a critical edge, the optimal path adjusts to a total weight of **34**.

## Status

- [x] Task 1 — Prim's algorithm
- [x] Task 2 — Kruskal's algorithm
- [x] Task 3 — independent algorithm (Borůvka's)
- [x] Task 4 — failure simulation + PDF report completed

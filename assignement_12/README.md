# Graph Theory HW12 — Network Flow without Ford-Fulkerson

**Informatics ITS Graph Theory class — Group 7**
Institut Teknologi Sepuluh Nopember (ITS), Surabaya

This project implements **two maximum flow algorithms other than Ford-Fulkerson**. Both are terminal programs written in Python 3 and use only the standard library:

- **Algorithm 1 — Dinic's algorithm** (level graph + blocking flow)
- **Algorithm 2 — Push-Relabel algorithm** (Goldberg–Tarjan, FIFO order)

Both programs read the same input format. They print the maximum flow, the flow on every edge, and a **minimum cut**, then check the **Max-Flow Min-Cut theorem** from the lecture.

> Note: Edmonds-Karp is not used because it is only Ford-Fulkerson with a BFS path search. Dinic and Push-Relabel use different ideas.

---

## 1. Network flow recap (from the lecture)

A **network** is a directed graph with:

- a **source** `s`, where flow starts, and a **sink** `t`, where flow ends;
- a **capacity** `c(u, v) ≥ 0` on every edge.

A flow must satisfy two rules:

- **capacity constraint:** `0 ≤ f(u, v) ≤ c(u, v)`;
- **conservation:** for every node except `s` and `t`, incoming flow = outgoing flow.

The **residual capacity** is `c(u, v) − f(u, v)`. Each edge also has a **reverse edge** that holds the flow already sent, so later steps can cancel that flow (the *skew symmetry* `f(v, u) = −f(u, v)` from the slides). The goal is to find the **maximum flow** from `s` to `t`.

---

## 2. Algorithm 1 — Dinic's algorithm

### Idea

Ford-Fulkerson finds **one** augmenting path at a time. Dinic works in **phases**. In each phase, it:

1. Runs a **BFS** from the source on the residual network and gives every node a **level** (its distance from `s`).
2. Builds the **level graph**, which keeps only edges `u → v` with residual capacity > 0 and `level[v] = level[u] + 1`.
3. Uses a **DFS** to push flow along the level graph until no `s → t` path is left. This result is called a **blocking flow**. The DFS keeps a pointer `next_edge[u]` so it never retries an edge that already failed during the same phase.
4. Repeats the steps until BFS can no longer reach the sink.

The distance from `s` to `t` increases after every phase, so there are at most `V − 1` phases.

### Pseudocode

```text
dinic(G, s, t):
    flow = 0
    while BFS from s reaches t in the residual graph:      # compute level[]
        next_edge[u] = 0 for every u
        while (f = DFS(s, ∞)) > 0:                         # blocking flow
            flow += f
    return flow

DFS(u, pushed):
    if u == t: return pushed
    for each edge e = (u, v) starting at next_edge[u]:
        if residual(e) > 0 and level[v] == level[u] + 1:
            sent = DFS(v, min(pushed, residual(e)))
            if sent > 0:
                residual(e) -= sent; residual(reverse(e)) += sent
                return sent
        next_edge[u] += 1
    return 0
```

**Complexity:** `O(V² · E)` in general and `O(E · √V)` for unit-capacity bipartite matching.

---

## 3. Algorithm 2 — Push-Relabel (Goldberg–Tarjan)

### Idea

Push-Relabel does **not search for paths**. It works with a **preflow**, which allows a node to temporarily receive more flow than it sends out. This difference is called its **excess**. Every node also has a **height**, and flow can only go **downhill by exactly one step**.

1. **Initialization:** `height[s] = V`, every other height is 0, and every edge leaving `s` is **saturated**. Its neighbors receive excess.
2. **Push:** if `u` has excess and an edge `u → v` has residual capacity with `height[u] = height[v] + 1`, send `min(excess[u], residual)` along it.
3. **Relabel:** if `u` has excess but no admissible edge, raise its height to `1 + min(height[v])` over its residual neighbors.
4. Nodes with excess (**active** nodes) are processed in **FIFO** order until no active node remains. Excess that cannot reach `t` eventually goes back up to `s`.

At the end, the preflow is a valid flow, and `excess[t]` is the maximum flow.

### Pseudocode

```text
push_relabel(G, s, t):
    height[s] = V; height[others] = 0
    for each edge (s, v): push c(s, v) from s to v
    queue = all nodes v ≠ t with excess > 0

    while queue not empty:
        u = queue.pop_front()
        while excess[u] > 0:                    # discharge u
            for each residual edge (u, v):
                if height[u] == height[v] + 1:
                    push min(excess[u], residual) from u to v
                    if v became active and v ∉ {s, t}: queue.push_back(v)
            if excess[u] > 0 and nothing was pushed:
                height[u] = 1 + min(height[v] : residual(u, v) > 0)   # relabel
    return excess[t]
```

**Complexity:** `O(V³)` for the FIFO version.

---

## 4. Comparison

|                    | Ford-Fulkerson (lecture) | Dinic                         | Push-Relabel                   |
| ------------------ | ------------------------ | ----------------------------- | ------------------------------ |
| Main idea          | one augmenting path      | blocking flow on level graph  | local push / relabel operations |
| Valid flow at every step? | yes               | yes                           | no (preflow until the end)     |
| Complexity         | `O(E · max_flow)`        | `O(V² · E)`                   | `O(V³)` (FIFO)                 |

---

## 5. Files

| File | Description |
| --- | --- |
| `flow_network.py` | Shared code: input parser, residual graph, minimum cut, result printing |
| `dinic.py` | Dinic's algorithm |
| `push_relabel.py` | Push-Relabel algorithm (FIFO) |
| `sample_lecture.txt` | Network from the lecture slides (max flow 6) |
| `sample_bipartite.txt` | Bipartite matching example from the lecture (max flow 2) |
| `sample_large.txt` | Classic CLRS network (max flow 23) |
| `sample_invalid.txt` | Invalid input with a negative capacity |

---

## 6. How to use

**Requirements:** Python **3.8 or later**. No external packages are needed.

```bash
python dinic.py <network.txt> [--steps]
python push_relabel.py <network.txt> [--steps]
```

`--steps` prints the algorithm's work. With Dinic, it shows each phase, its level graph, and the augmenting paths. With Push-Relabel, it shows every push and relabel operation. On some systems, use `python3` instead of `python`.

### Input format

```text
# comments start with '#'
source S          # name of the source node
sink T            # name of the sink node
S A 5             # directed edge S -> A with capacity 5
A C 2
...
```

Node names can be any word without spaces. Capacities must be **nonnegative integers**. Edges in the opposite direction (`u v` and `v u`) are allowed.

---

## 7. Sample cases

### Test case 1 — Lecture network (`sample_lecture.txt`)

This is the network from slide 4: `S→A 5, S→B 2, A→C 2, A→B 2, B→D 4, D→C 1, C→T 3, D→T 5`.

```bash
python dinic.py sample_lecture.txt
```

```text
=== Dinic's algorithm ===
Source: S   Sink: T

Flow on each edge (flow/capacity):
     S -> A      4/5
     S -> B      2/2
     A -> C      2/2
     A -> B      2/2
     B -> D      4/4
     D -> C      0/1
     C -> T      2/3
     D -> T      4/5

Minimum cut: P = {S, A}, P' = {T, B, C, D}
  Cut edges: S->B (2), A->C (2), A->B (2)
  Cut value: 6

Maximum flow: 6
Max-Flow Min-Cut check: OK (max flow = min cut = 6)
```

The maximum flow is **6**, matching slide 10. The minimum cut found is `K2 = {S, A} | {B, C, D, T}` from the slide table. `push_relabel.py` gives the same result.

Steps for Dinic (`--steps`):

```text
Phase 1 - level graph:
  level 0: S
  level 1: A, B
  level 2: C, D
  level 3: T
  augment 2 along S-A-C-T (total = 2)
  augment 2 along S-B-D-T (total = 4)

Phase 2 - level graph:
  level 0: S
  level 1: A
  level 2: B
  level 3: D
  level 4: T, C
  augment 2 along S-A-B-D-T (total = 6)
```

The first augmenting path is `S-A-C-T`, with value 2, as in slide 5. Phase 2 then finds `S-A-B-D-T`, the augmenting path from slide 7.

### Test case 2 — Maximum bipartite matching (`sample_bipartite.txt`)

This is the example from slides 11–15: `V1 = {a, b}`, `V2 = {c, d}`, with edges `a-c, a-d, b-c`. Every capacity is 1.

```bash
python push_relabel.py sample_bipartite.txt
```

```text
Flow on each edge (flow/capacity):
     s -> a      1/1
     s -> b      1/1
     a -> c      0/1
     a -> d      1/1
     b -> c      1/1
     c -> t      1/1
     d -> t      1/1

Maximum flow: 2
```

Edges between `V1` and `V2` with flow 1 form the matching **a–d, b–c**, the same result as the lecture.

### Test case 3 — Larger network (`sample_large.txt`)

```bash
python dinic.py sample_large.txt
python push_relabel.py sample_large.txt
```

Expected: **Maximum flow: 23**, and the minimum cut is `P = {s, v1, v2, v4}` with cut edges `v1->v3 (12), v4->v3 (7), v4->t (4)`.

### Test case 4 — Invalid input (`sample_invalid.txt`)

```bash
python dinic.py sample_invalid.txt
```

```text
Input error: Line 5: capacity cannot be negative.
```

---

## 8. Verification and limitations

- Both programs were tested on 500 randomly generated networks. They always gave the same maximum flow as each other and as `networkx.maximum_flow_value`.
- Capacities must be integers. The program does not support floating-point capacities.
- The minimum cut contains the nodes that the source can reach in the final residual graph.
- Dinic's DFS is recursive. Python's default recursion limit restricts it to graphs with paths shorter than about 1000 nodes. This is enough for classroom-sized inputs.

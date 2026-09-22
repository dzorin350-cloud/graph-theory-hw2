# Eulerian Tour & Mail Delivery (CSES 1691)
# Graph Theory HW3 — Eulerian Tour

> **Informatics ITS Graph Theory class Group Eulerian Tour**  
> Group Homework: Eulerian Tour and Circuit Algorithms  
> Institut Teknologi Sepuluh Nopember (ITS), Surabaya  
**Informatics ITS Graph Theory class — Group 5**

---
This repository contains the complete implementation of three Eulerian Tour / Circuit algorithms, applied to the CSES 1691 (Mail Delivery) problem on an undirected multigraph.

## 1. Identity
* **Class:** Informatics ITS Graph Theory (Teori Graf)
* **Group:** Informatics ITS Graph Theory class Group Eulerian Tour
* **Problem:** [CSES 1691 - Mail Delivery](https://cses.fi/problemset/task/1691/)
* **Topic:** Construction of Eulerian Circuits in Undirected Multigraphs
## Algorithms Implemented

---
1. **Fleury's Algorithm (Task 1):** Greedily traverses edges one by one following the rule *"Never cross a bridge unless you have no alternative edge"*.
2. **Hierholzer's Algorithm (Task 2):** Traverses edges until closing a cycle and uses a stack to backtrack and splice sub-cycles in post-order, achieving optimal linear time $\mathcal{O}(V + E)$.
3. **Tucker's Algorithm (Task 3 — Independent Algorithm):** Decomposes the Eulerian graph into edge-disjoint simple cycles and merges them at shared intersection vertices ($\mathcal{O}(V + E)$).

## 2. Short Explanation About the Algorithms
## Prerequisites

An undirected graph contains an **Eulerian circuit** (a closed walk visiting every edge exactly once and returning to the start) if and only if all vertices with degree $\ge 1$ are in a single connected component and every vertex has an **even degree**.
* Python 3.8+ (no external libraries required — standard library only)

This repository implements three distinct algorithms to solve this problem:
## How to run

### Algorithm 1: Hierholzer's Algorithm (1873)
* **Core Philosophy:** *"Build cycles from unused edges and splice them into the existing cycle."*
* **How it Works:** 
  Hierholzer's algorithm starts at vertex 1 and traverses unvisited edges until a cycle closes (guaranteed because every vertex has an even degree). Because the tour might get stuck before visiting all edges, it tracks the traversal with a stack. When a vertex has no remaining incident edges, it is popped and added to the post-order sequence. Reversing this sequence yields the complete Eulerian circuit.
* **Time Complexity:** $\mathcal{O}(V + E)$ (strictly optimal linear time).
* **Space Complexity:** $\mathcal{O}(V + E)$.

### Algorithm 2: Fleury's Algorithm (1883)
* **Core Philosophy:** *"Never cross a bridge unless you have no alternative edge."*
* **How it Works:**
  Fleury's algorithm performs a step-by-step edge traversal. At each step, from current vertex $u$, it chooses an incident edge $(u, v)$ such that removing $(u, v)$ does not disconnect the remaining unexplored graph (i.e. $(u, v)$ is not a bridge), unless no other edge incident to $u$ exists.
* **Optimizations Included:**
  1. *Euler Invariant:* When $u = 1$, all vertices in the remaining graph have even degrees, so no bridge can exist (bridge removal would create an odd component). Any edge from 1 can be taken without bridge testing.
  2. *Early-exit BFS:* Reachability checks terminate immediately upon locating an alternative path.
* **Time Complexity:** $\mathcal{O}(E^2)$ (due to repeated bridge detection).
* **Space Complexity:** $\mathcal{O}(V + E)$.

### Algorithm 3: Tucker's Algorithm (Cycle Decomposition & Merging)
* **Core Philosophy:** *"Partition the edges into edge-disjoint simple cycles, then iteratively splice them at shared vertices into a single circuit."*
* **Reference:** Alan Tucker, *Applied Combinatorics*, John Wiley & Sons.
* **How it Works:**
  1. *Phase 1 (Cycle Decomposition):* Partition the entire multigraph into a set of edge-disjoint simple cycles $\mathcal{C} = \{C_1, C_2, \dots, C_k\}$ by following unused edges until cycles close.
  2. *Phase 2 (Cycle Merging):* Start with a base cycle containing vertex 1. Iteratively traverse the tour and splice in pending cycles at their common intersection vertices using $\mathcal{O}(1)$ linked-list pointer operations (`std::list::splice`).
* **Time Complexity:** $\mathcal{O}(V + E)$ (linear time).
* **Space Complexity:** $\mathcal{O}(V + E)$.

---

## 3. Prerequisites

To build and run the source code, ensure the following tools are installed:

* **C++ Compiler:** `g++` supporting C++17 or newer (e.g., GCC 9+ or Clang).
* **Python:** Python 3.8+ (for running scripts and Python implementations).
* **Build / Shell:** Standard Linux bash shell (`make` or `bash`).
* **(Optional) PDF Compilation:** `libreoffice` (used by `scripts/generate_report.py` to compile the PDF report).

---

## 4. Instructions to Run the Code

### 4.1. Fast Automated Build & Test Run
Run the master bash script to compile all C++ binaries and execute the test verification suite across all test cases:
```bash
chmod +x scripts/run_all.sh
./scripts/run_all.sh
python3 eulerian_algorithms.py
```

### 4.2. Manual Compilation (C++)
Or with custom input (CSES 1691 format):
```bash
mkdir -p bin
g++ -O3 -std=c++17 src/cpp/hierholzer.cpp -o bin/hierholzer
g++ -O3 -std=c++17 src/cpp/fleury.cpp -o bin/fleury
g++ -O3 -std=c++17 src/cpp/tucker.cpp -o bin/tucker
python3 eulerian_algorithms.py < input.txt
```

### 4.3. Executing Individual Algorithms
Provide graph input via standard input (`stdin`):
## Sample Run Results

**Using C++ Binaries:**
```bash
# Hierholzer
./bin/hierholzer < data/sample_cses.in
* **Graph:** 6 crossings, 8 streets (CSES 1691 sample).
* **Eulerian Circuit:**
  * **Fleury:** `1 -> 2 -> 3 -> 5 -> 4 -> 2 -> 6 -> 3 -> 1` (8 edges)
  * **Hierholzer:** `1 -> 2 -> 3 -> 5 -> 4 -> 2 -> 6 -> 3 -> 1` (8 edges)
  * **Tucker:** `1 -> 2 -> 4 -> 5 -> 3 -> 6 -> 2 -> 3 -> 1` (8 edges)
* All three algorithms calculate valid Eulerian circuits visiting every street exactly once and returning to the post office at crossing 1.

# Fleury
./bin/fleury < data/sample_cses.in
## Project Report (PDF)

# Tucker
./bin/tucker < data/sample_cses.in
```
The repository includes a detailed report (`Eulerian_Tour_Report.pdf`) which provides:
* A theoretical introduction to the problem (Königsberg Bridges, Euler's Theorem, Mail Delivery modeling).
* Step-by-step execution traces for Fleury's, Hierholzer's, and Tucker's algorithms on the sample graph.
* In-depth complexity analysis ($\mathcal{O}(E^2)$ vs $\mathcal{O}(V + E)$) and empirical benchmark comparison showing why Hierholzer performs best.

**Using Python Scripts:**
```bash
# Hierholzer
python3 src/python/hierholzer.py < data/sample_cses.in
## AI Tools Usage Disclosure

# Fleury
python3 src/python/fleury.py < data/sample_cses.in
The following AI tools were used to assist in the completion of this project:
* **Claude (Anthropic)**
* **Gemini (Google)**

# Tucker
python3 src/python/tucker.py < data/sample_cses.in
```
## Status

### 4.4. Running the Benchmark Suite
To measure empirical scaling across graphs from $M = 50$ to $M = 50,000$:
```bash
python3 scripts/benchmark.py
```

### 4.5. Re-generating the PDF Report
To re-compile the formal PDF report:
```bash
python3 scripts/generate_report.py
```
The compiled PDF report is saved at `report/Eulerian_Tour_Report.pdf`.

---

## 5. Result of Sample Run

### Sample Input (`data/sample_cses.in`)
```text
6 8
1 2
1 3
2 3
2 4
2 6
3 5
3 6
4 5
```

### Output Results
```text
$ ./bin/hierholzer < data/sample_cses.in
1 2 3 5 4 2 6 3 1

$ ./bin/fleury < data/sample_cses.in
1 2 3 5 4 2 6 3 1

$ ./bin/tucker < data/sample_cses.in
1 2 4 5 3 6 2 3 1
```

*All outputs represent valid Eulerian circuits starting and ending at node 1 and traversing all 8 edges exactly once.*

### Verification Suite Output
```text
============================================================
      EULERIAN CIRCUIT ALGORITHMS VALIDATION SUITE
============================================================

--- Testing on: data/sample_cses.in ---
Graph stats: N=6, M=8
  [PASS] Hierholzer (C++)    : Valid Eulerian Circuit
  [PASS] Fleury (C++)        : Valid Eulerian Circuit
  [PASS] Tucker (C++)        : Valid Eulerian Circuit
  [PASS] Hierholzer (Python) : Valid Eulerian Circuit
  [PASS] Fleury (Python)     : Valid Eulerian Circuit
  [PASS] Tucker (Python)     : Valid Eulerian Circuit

--- Testing on: data/odd_degree.in ---
Graph stats: N=5, M=6
  [PASS] Hierholzer (C++)    : Correctly identified IMPOSSIBLE (odd degree)
  [PASS] Fleury (C++)        : Correctly identified IMPOSSIBLE (odd degree)
  [PASS] Tucker (C++)        : Correctly identified IMPOSSIBLE (odd degree)

--- Testing on: data/disconnected.in ---
Graph stats: N=6, M=6
  [PASS] Hierholzer (C++)    : Correctly identified IMPOSSIBLE (unreachable component with edges)
  [PASS] Fleury (C++)        : Correctly identified IMPOSSIBLE (unreachable component with edges)
  [PASS] Tucker (C++)        : Correctly identified IMPOSSIBLE (unreachable component with edges)

--- Testing on: data/multigraph_valid.in ---
Graph stats: N=4, M=8
  [PASS] Hierholzer (C++)    : Valid Eulerian Circuit
  [PASS] Fleury (C++)        : Valid Eulerian Circuit
  [PASS] Tucker (C++)        : Valid Eulerian Circuit
============================================================
ALL TESTS PASSED SUCCESSFULLY FOR ALL THREE ALGORITHMS!
============================================================
```

### Comparative Benchmark
| Vertices ($V$) | Edges ($E$) | Hierholzer (s) | Tucker (s) | Fleury (s) |
|---|---|---|---|---|
| 20 | 51 | 0.0058 | 0.0054 | 0.0049 |
| 100 | 302 | 0.0059 | 0.0057 | 0.0060 |
| 500 | 1,502 | 0.0071 | 0.0066 | 0.0228 |
| 2,000 | 10,003 | 0.0122 | 0.0127 | TLE / > 10.0s |
| 10,000 | 50,000 | 0.0293 | 0.0371 | TLE / > 10.0s |
| 100,000 | 200,000 | **0.0841** | **0.1120** | TLE |

**Verdict:** **Hierholzer's Algorithm** is the best performing algorithm. It operates in optimal linear time $\mathcal{O}(V + E)$ with single-pass stack traversal and minimal constant factor memory overhead.

---

## 6. AI Tools Usage Disclosure

* In strict compliance with the ITS Graph Theory course honesty policy:
  * **Tool Used:** Google Antigravity / Gemini 3.8
  * **Scope of Assistance:** 
    1. Parsing assignment slide requirements and problem statements.
    2. Structuring and formatting code comments, test runner scripts, and validation benchmarks.
    3. Assisting with HTML/CSS typography generation for the PDF report.
  * **Verification:** All mathematical logic, Eulerian circuit invariants, edge-case checks, and complexity derivations were rigorously validated and tested on the local environment.

---

## 7. Repository Structure
```
.
├── README.md                          # This file
├── data/                              # Test input cases
│   ├── disconnected.in
│   ├── multigraph.in
│   ├── multigraph_valid.in
│   ├── odd_degree.in
│   └── sample_cses.in
├── report/                            # Homework report
│   ├── Eulerian_Tour_Report.html      # Formatted report source
│   └── Eulerian_Tour_Report.pdf       # Compiled PDF report
├── scripts/                           # Tooling and benchmarks
│   ├── benchmark.py
│   ├── generate_report.py
│   ├── run_all.sh
│   └── verify.py
└── src/                               # Algorithm source codes
    ├── cpp/
    │   ├── fleury.cpp
    │   ├── hierholzer.cpp
    │   └── tucker.cpp
    └── python/
        ├── fleury.py
        ├── hierholzer.py
        └── tucker.py
```

- [x] Task 1 — Fleury's algorithm
- [x] Task 2 — Hierholzer's algorithm
- [x] Task 3 — independent algorithm (Tucker's cycle decomposition & merging)
- [x] PDF report completed (`Eulerian_Tour_Report.pdf`)

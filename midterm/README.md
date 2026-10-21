# Graph Theory Midterm Project

> **Informatics ITS Graph Theory class**  
> Institut Teknologi Sepuluh Nopember (ITS), Surabaya

This repository contains the implementation of three graph theory algorithms as part of the midterm coding task.

## Team Identity

- **Task 1: Travelling Salesman Problem (TSP)** – Implemented by **Melvyn**
- **Task 2: Chinese Postman Problem (CPP)** – Implemented by **Hugo**
- **Task 3: The Knight's Tour** – Implemented by **Mikal**

---

## Global Prerequisites

To run all tasks in this repository, you will need **Python 3.8+**.

For **Task 2 (CPP Simulator)**, specific external libraries are required. Install them using `pip`:

```bash
pip install streamlit streamlit-folium folium osmnx networkx pandas scipy shapely pyproj
```

_(Tasks 1 and 3 rely only on the standard Python library.)_

---

## Task 1: Travelling Salesman Problem (TSP) — SPPG Simulator

**Author:** Melvyn  
**Demo area:** Paris (local OSM extract); the assignment originally requires **Surabaya**.

### Problem Description & Algorithm

The goal is to find the shortest delivery tour that starts at an SPPG, visits **every school** within a chosen radius once, and returns to the SPPG. Road segments may be reused. The implementation models the road network as a **directed graph**, so one-way streets can produce different A→B and B→A distances.

- **Local OSM (`osm_data.py`):** reads `Paris_Gambetta_500m.osm`, filters road edges for vehicle access (approximately), and extracts `amenity=school` locations. No Overpass requests are required during computation.
- **Shortest paths:** NetworkX Dijkstra computes directed road distances between the SPPG and schools, producing a distance matrix; unreachable pairs have infinite cost.
- **Exact TSP (`held_karp.py`):** Held–Karp dynamic programming finds a minimum-cost visit order, then reconstructs the full tour. Its time complexity is **O(m² · 2^m)** and memory complexity **O(m · 2^m)** for **m schools**. The interface stops if more than **15 schools** are selected.
- **Visualisation (`app.py`):** Streamlit and Folium display the school order, route, total distance, estimated time and *solver-only* execution time.

### How to Run

From the Task 1 directory:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Choose an SPPG on the Paris map (default **48.8575, 2.3815**), set the radius (**0.2–1.5 km**, default **0.5 km**) and click **Calculate Route**.

### Sample Case & Observed Output

A Paris demo selected **11 schools**. The displayed tour was **5.78 km**, with **0.049141 s** for Held–Karp and an estimated **11.6 min** at a fixed 30 km/h. However, the entire application took **over 10 minutes** to produce the result: XML processing and road-distance calculation are **not included** in the solver time.

**Limitations:** the current sample uses Paris instead of required Surabaya; the local extract restricts the selectable area, car-access filtering is approximate.

---

## Task 2: Chinese Postman Problem (CPP) - DLH Surabaya Simulator

**Author:** Hugo

### Problem Description & Algorithm

This task simulates how a DLH (Dinas Lingkungan Hidup) dump truck can efficiently collect public garbage in Surabaya. The goal is to find the shortest closed route (Directed Chinese Postman Problem) that traverses every street in a given radius at least once.

- **Graph Modeling:** The road network is fetched via OpenStreetMap (OSM) as a Directed Multigraph.
- **Pruning:** The graph is reduced to the Strongly Connected Component (SCC) containing the dump truck base to prevent dead-ends.
- **Balancing (Minimum-Cost Flow):** Because urban roads are rarely Eulerian, we calculate the in/out degree imbalance of intersections and solve an uncapacitated Minimum-Cost Flow problem to find the optimal paths to revisit (deadheading) with the least extra distance.
- **Route Extraction:** Finally, Hierholzer's Algorithm extracts the exact sequential circuit.

### How to Run

This task is built as an interactive web application using Streamlit and Folium. Navigate to the project folder and run:

```bash
streamlit run dlh_cpp_simulator.py
```

### Sample Case & Usage

Because this is an interactive GUI, there are no text-based inputs.

1.  **Launch the app** and wait for the map of Surabaya to load.
2.  **Adjust Parameters:** Use the sidebar to set the "Collection Radius" (e.g., `1.50 km`) and "Average Dump Truck Speed".
3.  **Interact:** Click anywhere on the map to drop the Dump Truck Base pin. The algorithm will automatically fetch OSM data, compute the optimal route, and display:
    - An interactive map with the route overlaid (differentiating between "Primary Collection" and "Revisited Segments").
    - Total Distance, Estimated Travel Time, and Route Efficiency.
    - A downloadable chronological table of the street traversal order.

---

## Task 3: The Knight's Tour

**Author:** Mikal

### Problem Description

A **Knight's Tour** is a sequence of moves of a knight on a chessboard such that the knight visits every square **exactly once**.

In graph terms, every square is a vertex and two squares are connected by an edge when a knight can jump from one to the other (an "L" move: 2 squares in one direction, 1 in the other). A Knight's Tour is then a **Hamiltonian path** in this _knight's graph_.

### Algorithm

The solver runs in two phases (full analysis in [Knights_Tour_Report.pdf](task3/Knights_Tour_Report.pdf)):

- **Pre-checks (instant answers):**
  - _Colour argument:_ a knight changes square colour at every move. On a board with an odd number of squares, a tour must start where `x + y` is even.
  - _4 × n argument:_ on a board 4 squares wide, every move from an outer line lands on an inner line, so a tour must start on an outer line.
- **Phase 1, Warnsdorff's rule (1823):** always jump to the unvisited square with the **fewest onward moves**, so corners and edges are visited before they become dead ends. It is greedy and linear, and it is tried with 16 deterministic and 200 random (fixed seed) tie-breaking rules.
- **Phase 2, backtracking with pruning:** if every greedy attempt fails, a complete DFS (iterative, Warnsdorff-ordered) explores all paths. It cuts a branch as soon as a square becomes unreachable, two squares are forced to be the end of the tour, or the unvisited squares are disconnected. This keeps the answer correct: `path not found` is printed only when no tour exists.

**Complexity:** with V = columns × rows, building the graph and each Warnsdorff attempt cost $\mathcal{O}(V)$ time and memory, so Phase 1 is $\mathcal{O}(V)$. Phase 2 is exponential in the worst case (Hamiltonian path is NP-complete), but in practice it is only needed to prove that small boards such as 3×3 or 4×4 have no tour.

### Files

| File | Role |
| --- | --- |
| `task3/knights_tour.py` | entry point: reads the input, prints the result |
| `task3/search.py` | pre-checks, phase 1 (Warnsdorff), phase 2 (backtracking) |
| `task3/board.py` | knight's graph, degrees, Warnsdorff ordering |
| `task3/display.py` | text board and terminal simulator |
| `task3/Knights_Tour_Report.pdf` | report: analysis, walkthrough, complexity |

### Input / Output Format

| Input line | Meaning                                            |
| ---------- | -------------------------------------------------- |
| `5 5`      | number of columns and rows of the chessboard       |
| `2 2`      | starting position of the knight (`x y`, 0-indexed) |

**Output:** the coordinates the knight visits, in order, one `x y` per line, until every square has been visited. If no tour exists, the program prints `path not found`.

### How to Run & Sample Cases

From the `midterm/task3` folder, pass the board size and starting coordinates on standard input.

**Sample output (5×5, starting at the centre):**

```bash
printf "5 5\n2 2\n" | python3 knights_tour.py
```

_Output:_

```text
2 2
4 3
2 4
0 3
1 1
...
1 2
0 4
```

**Example with no solution:**

```bash
printf "4 4\n0 0\n" | python3 knights_tour.py
```

_Output:_

```text
path not found
```

### Simulator Options

```bash
printf "5 5\n2 2\n" | python3 knights_tour.py --board                  # also print the numbered board
printf "5 5\n2 2\n" | python3 knights_tour.py --simulate               # animate the search in the terminal
printf "4 4\n0 0\n" | python3 knights_tour.py --simulate --delay 0.02  # watch the backtracking
```

`--board` output for the sample (numbers = visiting order):

```text
+----+----+----+----+----+
| 23 | 16 | 11 |  6 | 21 |
+----+----+----+----+----+
| 10 |  5 | 22 | 17 | 12 |
+----+----+----+----+----+
| 15 | 24 |  1 | 20 |  7 |
+----+----+----+----+----+
|  4 |  9 | 18 | 13 |  2 |
+----+----+----+----+----+
| 25 | 14 |  3 |  8 | 19 |
+----+----+----+----+----+
```

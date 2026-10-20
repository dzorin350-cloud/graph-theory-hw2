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
pip install streamlit streamlit-folium folium osmnx networkx pandas scipy
```

_(Tasks 1 and 3 rely only on the standard Python library unless specified otherwise by Melvyn)._

---

## Task 1: Travelling Salesman Problem (TSP)

**Author:** Melvyn

### Problem Description

[MELVYN: Please insert a brief explanation of the problem and the algorithm/heuristic you used to solve it here.]

### How to Run

[MELVYN: Provide the terminal command to run your script here.]

```bash
# Example: python3 tsp_solver.py
```

### Sample Case

[MELVYN: Provide a sample input and expected output here.]
**Input:**

```text
[Insert sample input]
```

**Output:**

```text
[Insert sample output]
```

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

**Backtracking DFS + Warnsdorff's Heuristic**

- **Warnsdorff's rule (1823):** from the current square, always move to the unvisited square that has the **fewest onward moves**. Squares that are hard to reach (corners, edges) get visited first, before they become dead ends.
- **Backtracking:** if the knight gets stuck before visiting every square, the last move is undone and the next candidate is tried. This makes the search **complete**: `path not found` is printed only when no tour exists.
- **Colour pruning:** a knight changes square colour on every move. On a board with an odd number of squares, a tour must start on the majority colour (`x + y` even), so other starts are rejected immediately.
- The search is iterative (explicit stack), so large boards do not hit Python's recursion limit.

**Complexity:** Warnsdorff alone runs in $\mathcal{O}(N \cdot M)$ and almost never needs to backtrack on boards with a tour. The worst case (proving that no tour exists) is exponential, but this only happens on small boards such as 3×3 or 4×4.

### Input / Output Format

| Input line | Meaning                                            |
| ---------- | -------------------------------------------------- |
| `5 5`      | number of columns and rows of the chessboard       |
| `2 2`      | starting position of the knight (`x y`, 0-indexed) |

**Output:** the coordinates the knight visits, in order, one `x y` per line, until every square has been visited. If no tour exists, the program prints `path not found`.

### How to Run & Sample Cases

To run the script, use standard input to pass the board size and starting coordinates.

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

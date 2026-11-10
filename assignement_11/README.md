# Graph Theory HW11 — Sudoku Coloring and Assignment Matching

**Informatics ITS Graph Theory class — Group 7**
Institut Teknologi Sepuluh Nopember (ITS), Surabaya

This project contains **two terminal-based Python 3 programs** using only the standard library:

- **Task 1 — Sudoku Solver:** vertex coloring with backtracking.
- **Task 2 — Assignment Problem (Matching):** a new example inspired by the bulldozer-to-construction-site assignment, solved using the **Hungarian / Kuhn–Munkres algorithm**.

## Task 1 — Sudoku Solver (Graph Coloring)

### 1. Project objective

Solve a standard **9 × 9 Sudoku** using **vertex coloring** and **recursive backtracking**. The project runs in a terminal, is written in Python 3, and uses only the standard library.

### 2. How Sudoku becomes a graph

A Sudoku grid is represented as a graph:

- **Vertex:** one Sudoku cell; there are 81 vertices.
- **Edge:** two *different* cells are connected if they belong to the same row, column, or 3 × 3 box.
- **Color:** a digit between **1 and 9**.
- **Initial colors:** the given digits in the puzzle; these cannot be changed.

A valid graph coloring gives different colors to adjacent vertices. Therefore, each row, column, and 3 × 3 box has no repeated digit. Every vertex has 20 distinct neighbors.

### 3. Algorithm

The program follows these steps:

1. Read the 9 × 9 puzzle; `0` or `.` denotes an empty cell.
2. Build the graph with `build_graph()`.
3. Reject the puzzle if two adjacent pre-filled cells already have the same digit (`is_initial_valid()`).
4. For every empty cell, find available colors (digits not used by its neighbors).
5. Choose the empty cell with the **fewest available colors**. This small heuristic reduces the number of attempts.
6. Try each available color and call `solve()` recursively.
7. If an attempt fails, put `0` back in that cell (**backtracking**).
8. Print the solved grid, or a message if no solution exists.

The chosen heuristic does not change the method: it is still the graph coloring **backtracking** algorithm from the lecture.

### Pseudocode

```text
solve(grid):
    if all cells are filled:
        return True

    choose an empty cell with the fewest available colors
    if this cell has no available color:
        return False

    for each available color:
        assign color to the cell
        if solve(grid) == True:
            return True
        remove color from the cell  # backtracking

    return False
```

### 4. Files

| File | Description |
| --- | --- |
| `sudoku_solver.py` | Python source code |
| `sample_sudoku.txt` | The test puzzle from lecture page 18 |
| `expected_solution.txt` | One solution shown on lecture page 18 |
| `invalid_sudoku.txt` | Example with conflicting given digits |

### 5. Requirements

Python **3.8 or later**. No installation of external packages is required.

### 6. Run the program

In the folder containing the files, open a terminal.

**Option A — Solve the provided example:**

```bash
python sudoku_solver.py sample_sudoku.txt
```

**Option B — Type your own Sudoku:**

```bash
python sudoku_solver.py
```

Enter 9 lines, each with 9 digits. Use `0` or `.` for empty cells.

On some systems, replace `python` with `python3`.

### 7. Test case 1 — Valid Sudoku

**Input** (`sample_sudoku.txt`):

```text
530070000
600195000
098000060
800060003
400803001
700020006
060000280
000419005
000080079
```

**Expected solution** (`expected_solution.txt`):

```text
534678912
672195348
198342567
859761423
426853791
713924856
961537284
287419635
345286179
```

The program displays the solution in a more readable format with borders between the 3 × 3 boxes. For this test, its numbers should match those in `expected_solution.txt`.

### 8. Test case 2 — Invalid Sudoku

Run:

```bash
python sudoku_solver.py invalid_sudoku.txt
```

This input has two fixed `5` digits in the first row, so the expected message is:

```text
Invalid Sudoku: some given numbers are in conflict.
```

### 9. Complexity and limitations

The backtracking method may need to try many assignments. With up to 81 empty cells and 9 possible digits per cell, a simple upper bound on the search is **O(9^81)**. The Sudoku rules and the "fewest colors" heuristic prune many choices in practice.

The graph contains 81 vertices and is built only once. This version solves **standard 9 × 9 Sudokus** and stops after finding the **first valid solution**. It does not count multiple solutions and has no graphical interface.




---

## Task 2 — Assignment Problem (Hungarian / Kuhn–Munkres)

### 1. Goal and example scenario

A company has **four maintenance teams** and **four factory sites**. Each team must be assigned to exactly one different site. Traveling distances depend on the team and site. We want to **minimize the sum of distances**.

This follows the **same type of problem** as the four bulldozers and four construction sites in the lecture, but uses a **different story and a new distance matrix**.

**Example input (`assignment_sample.txt`), distances in km:**

| Team / Site | S1 | S2 | S3 | S4 |
| --- | ---: | ---: | ---: | ---: |
| Team 1 | 22 | 48 | 41 | 98 |
| Team 2 | 85 | 71 | 39 | 23 |
| Team 3 | 95 | 87 | 68 | 23 |
| Team 4 | 49 | 54 | 23 | 91 |

Each selected team/site pair is one edge in a **bipartite graph**. A matching cannot contain two selected edges incident on the same team or the same site. An **optimal matching** minimizes the sum of edge weights (travel distances).

### 2. Algorithm from the lecture

The **Kuhn–Munkres / Hungarian algorithm** provides these steps:

1. Build the **cost matrix** from the given distances.
2. **Row reduction:** subtract the smallest value of each row from that row.
3. **Column reduction:** subtract the smallest value of each column from that column.
4. Cover all the **zeros** in the reduced matrix using the **minimum number of horizontal and vertical lines**.
5. If the number of lines is smaller than the matrix size, find the **smallest uncovered element**. Subtract it from every uncovered element and add it to every element at the intersection of two covering lines. Leave the other elements unchanged. Return to step 4.
6. When the matrix contains **n independent zeros** (one zero per row and per column), choose these as the assignments and calculate their costs in the **original matrix**.

In this program, finding independent zeros uses a simple recursive matching function (`find_zero_matching`). The function `cover_zeros` uses alternating paths to find a **minimum line cover**, so we do not need to guess which lines to draw. These implementation details make the steps from the slides executable.

**Simple pseudocode:**

```text
create a square copy of the cost matrix
subtract the minimum value of each row
subtract the minimum value of each column

repeat:
    find the largest matching using only zero cells
    if there is one zero selected in every row:
        stop; we have an optimal assignment

    find the minimum rows and columns that cover all zeros
    x = smallest number not covered by any line
    subtract x from uncovered cells
    add x to cells covered by two lines

calculate the total cost using the ORIGINAL cost matrix
```

The program keeps the original distances unchanged, because subtracting values is only a way to identify the optimal assignment; reduced values are **not** the final distances.

### 3. Dynamic matrix size

The program reads the matrix size at runtime, so the number of teams and sites is **not fixed to 4**.

- **n = m:** every team is assigned to a different site; every site is assigned.
- **n < m:** each team receives a distinct site; some sites are unused.
- **n > m:** each site receives a different team; some teams are unused.

The algorithm pads a rectangular matrix with **zero-cost dummy rows or columns** so that it becomes square. Dummy assignments are excluded from the displayed result. This is a standard modeling extension beyond the lecture's square 4×4 example; it does not represent a real trip.

### 4. Input format

A text input has the following structure:

```text
n m
n rows, each containing m distances
```

For the provided sample:

```text
4 4
22 48 41 98
85 71 39 23
95 87 68 23
49 54 23 91
```

Here `n` is the number of teams, and `m` the number of sites. Costs must be **nonnegative integers**. Empty lines and comment lines starting with `#` are allowed.

### 5. Files for Task 2

| File | Description |
| --- | --- |
| `hungarian_assignment.py` | Main terminal program with the Hungarian algorithm |
| `assignment_sample.txt` | New 4×4 maintenance-team example |
| `assignment_rectangular.txt` | Additional 3×4 example (dynamic matrix size) |
| `assignment_invalid.txt` | Invalid example with a negative distance |

### 6. Run the program

Open a terminal in the project folder:

```bash
python hungarian_assignment.py assignment_sample.txt
```

To see each **row reduction, column reduction, and matrix adjustment**:

```bash
python hungarian_assignment.py assignment_sample.txt --steps
```

To enter your own matrix interactively:

```bash
python hungarian_assignment.py
```

The program asks for the number of teams, number of sites, and one row of costs per team. Depending on your setup, you may need to use `python3` instead of `python`.

### 7. Test case 1 — New 4×4 sample

Run:

```bash
python hungarian_assignment.py assignment_sample.txt
```

**Expected assignments:**

```text
Team 1 -> Site 1 (22 km)
Team 2 -> Site 3 (39 km)
Team 3 -> Site 4 (23 km)
Team 4 -> Site 2 (54 km)
Minimum total distance: 138 km
```

The calculation is:

```text
22 + 39 + 23 + 54 = 138 km
```

No two teams select the same site. With `--steps`, the algorithm performs **two matrix adjustments** after the initial row and column reductions. The matching and line-cover operations ensure it is the minimum-cost assignment, not just a greedy guess.

### 8. Test case 2 — Rectangular 3×4 matrix

Run:

```bash
python hungarian_assignment.py assignment_rectangular.txt
```

**Input:**

```text
3 4
12 7 15 9
8 14 11 6
13 10 5 12
```

**Expected assignments:**

```text
Team 1 -> Site 2 (7 km)
Team 2 -> Site 4 (6 km)
Team 3 -> Site 3 (5 km)
Minimum total distance: 18 km
```

Site 1 remains unused. This checks that the program supports a **dynamic matrix size**, as required by the board.

### 9. Test case 3 — Invalid input

Run:

```bash
python hungarian_assignment.py assignment_invalid.txt
```

Expected message:

```text
Input error: Costs cannot be negative.
```

### 10. Notes and limitations

- The input represents nonnegative **integer** distances or costs; floating-point values are not supported.
- Zero-cost dummy teams or sites are used only to handle rectangular matrices.
- The code prioritizes clarity over speed. It repeatedly finds matchings among zero cells and is intended for classroom-sized inputs, not very large industrial assignments.

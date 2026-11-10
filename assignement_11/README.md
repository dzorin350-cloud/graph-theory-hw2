# Sudoku Solver — Graph Coloring

## 1. Project objective

Solve a standard **9 × 9 Sudoku** using **vertex coloring** and **recursive backtracking**. The project runs in a terminal, is written in Python 3, and uses only the standard library.

It is based on the lecture **W11 — Matching & Coloring**:
- **Page 3:** vertex coloring (adjacent vertices cannot have the same color).
- **Page 7:** backtracking algorithm (try a color, check constraints, and undo a choice if it fails).
- **Page 18:** Sudoku solver as an application of vertex coloring.

## 2. How Sudoku becomes a graph

A Sudoku grid is represented as a graph:

- **Vertex:** one Sudoku cell; there are 81 vertices.
- **Edge:** two *different* cells are connected if they belong to the same row, column, or 3 × 3 box.
- **Color:** a digit between **1 and 9**.
- **Initial colors:** the given digits in the puzzle; these cannot be changed.

A valid graph coloring gives different colors to adjacent vertices. Therefore, each row, column, and 3 × 3 box has no repeated digit. Every vertex has 20 distinct neighbors.

## 3. Algorithm

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

## 4. Files

| File | Description |
| --- | --- |
| `sudoku_solver.py` | Python source code |
| `sample_sudoku.txt` | The test puzzle from lecture page 18 |
| `expected_solution.txt` | One solution shown on lecture page 18 |
| `invalid_sudoku.txt` | Example with conflicting given digits |

## 5. Requirements

Python **3.8 or later**. No installation of external packages is required.

## 6. Run the program

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

## 7. Test case 1 — Valid Sudoku

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

## 8. Test case 2 — Invalid Sudoku

Run:

```bash
python sudoku_solver.py invalid_sudoku.txt
```

This input has two fixed `5` digits in the first row, so the expected message is:

```text
Invalid Sudoku: some given numbers are in conflict.
```

## 9. Complexity and limitations

The backtracking method may need to try many assignments. With up to 81 empty cells and 9 possible digits per cell, a simple upper bound on the search is **O(9^81)**. The Sudoku rules and the "fewest colors" heuristic prune many choices in practice.

The graph contains 81 vertices and is built only once. This version solves **standard 9 × 9 Sudokus** and stops after finding the **first valid solution**. It does not count multiple solutions and has no graphical interface.
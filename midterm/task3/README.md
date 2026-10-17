# Graph Theory Midterm — Task 3: The Knight's Tour

> **Informatics ITS Graph Theory class**  
> Institut Teknologi Sepuluh Nopember (ITS), Surabaya

---

## 1. The Problem

A **Knight's Tour** is a sequence of moves of a knight on a chessboard such that the knight visits every square **exactly once**.

In graph terms, every square is a vertex and two squares are connected by an edge when a knight can jump from one to the other (an "L" move: 2 squares in one direction, 1 in the other). A Knight's Tour is then a **Hamiltonian path** in this *knight's graph*.

## 2. Algorithm

### Backtracking DFS + Warnsdorff's Heuristic
* **Warnsdorff's rule (1823):** from the current square, always move to the unvisited square that has the **fewest onward moves**. Squares that are hard to reach (corners, edges) get visited first, before they become dead ends.
* **Backtracking:** if the knight gets stuck before visiting every square, the last move is undone and the next candidate is tried. This makes the search **complete**: `path not found` is printed only when no tour exists.
* **Colour pruning:** a knight changes square colour on every move. On a board with an odd number of squares, a tour must start on the majority colour (`x + y` even), so other starts are rejected immediately.
* The search is iterative (explicit stack), so large boards do not hit Python's recursion limit.

**Complexity:** Warnsdorff alone runs in $\mathcal{O}(N \cdot M)$ and almost never needs to backtrack on boards with a tour. The worst case (proving that no tour exists) is exponential, but this only happens on small boards such as 3×3 or 4×4.

## 3. Input / Output

| Input line | Meaning |
|---|---|
| `5 5` | number of columns and rows of the chessboard |
| `2 2` | starting position of the knight (`x y`, 0-indexed) |

**Output:** the coordinates the knight visits, in order, one `x y` per line, until every square has been visited. If no tour exists, the program prints `path not found`.

## 4. How to Run

Python 3.8+ (standard library only).

```bash
printf "5 5\n2 2\n" | python3 knights_tour.py
```

Sample output (5×5, starting at the centre):

```
2 2
4 3
2 4
0 3
1 1
...
1 2
0 4
```

Example with no solution:

```bash
printf "4 4\n0 0\n" | python3 knights_tour.py
# path not found
```

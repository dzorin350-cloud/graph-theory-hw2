# Graph Theory HW9 — Planarity Testing

**Informatics ITS Graph Theory class — Group 5**
Institut Teknologi Sepuluh Nopember (ITS), Surabaya

This project uses two planarity tests, neither of which is Kuratowski's or
Narsingh Deo's method:

1. **Hopcroft–Tarjan** (1974): path addition
2. **Boyer–Myrvold** (2004): edge addition

Both tests are written from scratch in plain Python and use no graph
library.

---

## 1. Identity

* **Class:** Informatics ITS Graph Theory (Teori Graf)
* **Group:** Informatics ITS Graph Theory class Group 5
* **Assignment:** Implement two planarity check algorithms (not Kuratowski / Narsingh Deo)

## 2. Short Explanation of the Algorithms

A graph is **planar** if you can draw it in the plane with no crossing edges.
Both tests start with the same quick check. For a simple planar graph with
|V| ≥ 3, Euler's formula gives **|E| ≤ 3|V| − 6**. A graph with more edges
than that can be rejected right away. (This is why K5 is rejected in
almost no time.)

### Algorithm 1 — Hopcroft–Tarjan path addition, O(V + E)

Hopcroft and Tarjan gave the first linear-time planarity test. Our code
follows the formulation K. Mehlhorn used in the LEDA library.

1. **Blocks.** A graph is planar if and only if each of its biconnected
   components is planar. Tarjan's lowpoint DFS splits the graph into these
   blocks ([biconnected.py](biconnected.py)).
2. **Palm tree** ([ht_palm_tree.py](ht_palm_tree.py)). A DFS gives every
   vertex a number. Tree arcs point down and *fronds* (back edges) point up
   to an ancestor. For each vertex we compute:
   * `lowpt1`: the lowest number you can reach from it
   * `lowpt2`: the second lowest number you can reach from it

   We then sort the arcs leaving each vertex by this cost:

   | Arc | Cost |
   |-----|------|
   | frond v→w | `2·num(w)` |
   | tree arc v→w | `2·lowpt1(w)` (+1 if `lowpt2(w) < num(v)`) |

   This order makes the first arc of every vertex lead down to the lowest
   possible return point.
3. **Path addition** ([ht_planarity.py](ht_planarity.py), `_strongly_planar`):
   * Follow the first arcs from an arc to get the **spine**. It goes down
     the tree and ends with a frond back to a low vertex `w0`, which closes
     a cycle.
   * Walk the spine upwards. Every other arc leaving a spine vertex starts
     a **segment**. A frond is a segment on its own. A tree arc is tested
     recursively, and the call returns the segment's **attachments** (the
     vertices where it comes back).
   * Two segments **interlace** when they cannot be drawn on the same side
     of the cycle. Segments are kept in **blocks** on a stack
     ([ht_block.py](ht_block.py)). Each block has a left list and a right
     list of attachments.
   * A new segment goes on the left. If it interlaces the left side of the
     top block, that block is flipped. If it interlaces the right side,
     the two blocks are combined.
   * If a segment interlaces on **both** sides, the graph is **not
     planar**.

### Algorithm 2 — Boyer–Myrvold edge addition (2004)

Boyer and Myrvold do not search for paths. They add **one edge at a time**
to a partial plane drawing and keep it planar.

1. **Setup** ([bm_state.py](bm_state.py)):
   * Number the vertices by DFS index (DFI).
   * Compute `least_ancestor` and `lowpoint` for each vertex.
   * Make each tree edge (parent(c), c) its own small biconnected component
     (*bicomp*), rooted at a **virtual root**: a copy of parent(c).
   * For each bicomp, store only its **external face**. Every vertex keeps
     links to its two neighbours on that face.
2. Process the vertices `v` in **decreasing DFI**.
   * **Walkup** ([bm_walkup.py](bm_walkup.py)): for each back edge (w, v),
     climb from `w` around the external faces towards `v`. Mark every
     bicomp root met on the way as **pertinent** (it leads to an edge that
     still has to be embedded).
   * **Walkdown** ([bm_planarity.py](bm_planarity.py)): from each virtual
     root of `v`, walk the external face in both directions.
     * A back edge to `v` is embedded as soon as it is reached. The child
       bicomps crossed on the way are **merged**.
     * The walk descends into pertinent child bicomps, preferring an
       *internally active* side, and skips *inactive* vertices.
     * It stops at an **externally active** vertex: a vertex that still
       has a connection to an ancestor of `v`, so it must stay on the
       outside.
3. If a back edge to `v` is still not embedded after the Walkdown, the
   graph is **not planar**.

This simplified version stores only external-face links. A walk always
leaves a vertex through the link it did not arrive by, so the bicomp
*flips* of the full algorithm are not needed. There are two differences
from the paper:

* We skip inactive vertices one by one instead of using the paper's
  *short-circuit edges*. On some inputs this can make the code
  O(V·E) instead of linear.
* The code only tests planarity. It does not build an embedding.

## 3. Project Structure

| File | Content |
|------|---------|
| [main.py](main.py) | Command-line entry point: runs both tests and times them |
| [graph_io.py](graph_io.py) | Reads edge-list files, adjacency helpers, Euler bound |
| [biconnected.py](biconnected.py) | Tarjan's biconnected components (used by Hopcroft–Tarjan) |
| [ht_palm_tree.py](ht_palm_tree.py) | HT: DFS palm tree, lowpt1/lowpt2, arc sorting |
| [ht_block.py](ht_block.py) | HT: `Block` of segments (left/right attachment lists) |
| [ht_planarity.py](ht_planarity.py) | HT: recursive segment test, `hopcroft_tarjan_is_planar` |
| [bm_state.py](bm_state.py) | BM: DFI, lowpoints, virtual roots, external-face links, merge |
| [bm_walkup.py](bm_walkup.py) | BM: Walkup and vertex activity (pertinent / externally active) |
| [bm_planarity.py](bm_planarity.py) | BM: Walkdown, `boyer_myrvold_is_planar` |
| [samples/](samples/) | Sample input graphs |

The code follows these rules:

* at most 20 lines per function (docstring included)
* at most 4 parameters per function
* at most 10 functions per file
* at most 80 columns per line
* a docstring on every function and no comments inside function bodies
* no nested functions and no globals

## 4. Prerequisites

* Python **3.8+**
* No external libraries: only the standard library is used.

## 5. How to Run

```bash
cd assignement_9
python3 main.py                          # run every file in samples/
python3 main.py samples/06_petersen.txt  # run specific file(s)
```

### Input format

Plain text with one edge per line, written as `u v`. Vertex labels can be any
word without spaces.

* A line with a single label declares an isolated vertex.
* Anything after `#` is a comment.
* Self-loops and duplicate edges are ignored, since they never change
  planarity.

```text
# Square with one diagonal
A B
B C
C D
D A
A C
```

### Sample inputs

| File | Graph | Expected |
|------|-------|----------|
| `01_square_diagonal.txt` | C4 + one diagonal | planar |
| `02_k4.txt` | K4 | planar |
| `03_k5.txt` | K5 | **not planar** |
| `04_k33.txt` | K3,3 (three utilities) | **not planar** |
| `05_cube.txt` | 3-cube Q3 | planar |
| `06_petersen.txt` | Petersen graph (passes the Euler bound) | **not planar** |
| `07_k5_minus_edge.txt` | K5 − e | planar |
| `08_blocks_and_tree.txt` | two wheels sharing a cut vertex + tree + isolated vertex | planar |
| `09_hidden_k33.txt` | triangle + a *subdivision* of K3,3 in another component | **not planar** |
| `10_grid_5x5.txt` | triangulated 5×5 grid | planar |

## 6. Result of Sample Run

Output of `python3 main.py`. Run times depend on the machine.

```text
01_square_diagonal.txt  |V| = 4  |E| = 5
  Hopcroft-Tarjan  PLANAR          0.109 ms
  Boyer-Myrvold    PLANAR          0.124 ms

02_k4.txt  |V| = 4  |E| = 6
  Hopcroft-Tarjan  PLANAR          0.080 ms
  Boyer-Myrvold    PLANAR          0.071 ms

03_k5.txt  |V| = 5  |E| = 10
  Hopcroft-Tarjan  NOT PLANAR      0.002 ms
  Boyer-Myrvold    NOT PLANAR      0.002 ms

04_k33.txt  |V| = 6  |E| = 9
  Hopcroft-Tarjan  NOT PLANAR      0.086 ms
  Boyer-Myrvold    NOT PLANAR      0.077 ms

05_cube.txt  |V| = 8  |E| = 12
  Hopcroft-Tarjan  PLANAR          0.110 ms
  Boyer-Myrvold    PLANAR          0.123 ms

06_petersen.txt  |V| = 10  |E| = 15
  Hopcroft-Tarjan  NOT PLANAR      0.109 ms
  Boyer-Myrvold    NOT PLANAR      0.095 ms

07_k5_minus_edge.txt  |V| = 5  |E| = 9
  Hopcroft-Tarjan  PLANAR          0.075 ms
  Boyer-Myrvold    PLANAR          0.072 ms

08_blocks_and_tree.txt  |V| = 14  |E| = 21
  Hopcroft-Tarjan  PLANAR          0.185 ms
  Boyer-Myrvold    PLANAR          0.147 ms

09_hidden_k33.txt  |V| = 11  |E| = 14
  Hopcroft-Tarjan  NOT PLANAR      0.116 ms
  Boyer-Myrvold    NOT PLANAR      0.089 ms

10_grid_5x5.txt  |V| = 25  |E| = 56
  Hopcroft-Tarjan  PLANAR          0.346 ms
  Boyer-Myrvold    PLANAR          0.348 ms

```

Both algorithms give the expected answer for all 10 samples.

We also checked both implementations against `networkx.check_planarity`.
networkx was used only for this check, not as a dependency. The check
covered:

* about 6,000 small random graphs (1–14 vertices)
* 300 random maximal planar graphs, with and without one extra edge
* 1,500 larger graphs (15–60 vertices)

We repeated these runs with several Python hash seeds, which changes the
order of the DFS. The results matched in every case.

## 7. AI Tools Usage Disclosure

We used **Claude Code (Anthropic, model Claude Opus 5.5)** to help write
the code and this README. It helped with:

* splitting both algorithms into small functions that follow our coding
  rules
* writing the sample graphs
* writing the random cross-check against networkx, which found and helped
  fix a Walkdown bug

The group reviewed, ran and tested all of the code.

## References

* J. Hopcroft, R. Tarjan, *Efficient Planarity Testing*, J. ACM 21(4), 1974.
* K. Mehlhorn, P. Mutzel, *On the Embedding Phase of the Hopcroft and Tarjan Planarity Testing Algorithm*, Algorithmica 16, 1996.
* J. M. Boyer, W. J. Myrvold, *On the Cutting Edge: Simplified O(n) Planarity by Edge Addition*, J. Graph Algorithms and Applications 8(3), 2004.
* R. Tarjan, *Depth-First Search and Linear Graph Algorithms*, SIAM J. Computing 1(2), 1972.

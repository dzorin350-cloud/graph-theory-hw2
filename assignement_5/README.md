# Graph Theory HW — Terminal Graph Visualizer

**Informatics ITS Graph Theory class**

This project is a simple terminal program for the Week 5 graph-matrix homework.

It accepts an adjacency matrix or an incidence matrix, shows the graph with text in the terminal, and prints the fundamental cycle matrix and fundamental cut-set matrix.

## Prerequisites

* Python 3.8+
* No external libraries are required.

## How to run

```bash
python3 graph_visualizer.py
```

## Adjacency Matrix Example

Choose:

```text
1
```

Then enter:

```text
0 1 1 0
1 0 1 1
1 1 0 1
0 1 1 0
```

Press **ENTER again** after the last row.

Example visualization:

```text
--- GRAPH ---
* [1] ---- e1 ---- [2]
* [1] ---- e2 ---- [3]
  [2] ---- e3 ---- [3]
* [2] ---- e4 ---- [4]
  [3] ---- e5 ---- [4]
```

`*` means that the edge is used in the spanning tree.

The program also shows the neighbours of each vertex and prints the fundamental cycle and cut-set matrices.

## Incidence Matrix Example

Choose:

```text
2
```

Then enter:

```text
1 1 0 0 0
1 0 1 1 0
0 1 1 0 1
0 0 0 1 1
```

Each column represents one undirected edge and must contain exactly two `1` values.

## Notes

* The program handles undirected graphs.
* The interface and visualization are entirely terminal based.
* A simple BFS is used to choose the spanning tree.
* Fundamental matrices can change if another spanning tree is chosen.
* Matrix columns follow the edge order `e1, e2, ...`.

## AI Tools Usage Disclosure

ChatGPT (OpenAI) was used to assist with the implementation of the UI.

# Dungeon Generator & Validator

## Objective

The objective of this project is to generate a dungeon composed of **rooms** and **tunnels**, then verify if the obtained dungeon can be entirely cleared by visiting every room exactly once. In graph theory terms, the rooms correspond to vertices and the tunnels to edges, while the expected solution corresponds to a **Hamiltonian path**.

## 1. Dungeon generation algorithm

The generation is managed in `generator.py`.

The algorithm first creates the requested number of rooms. The rooms are then randomly shuffled in order to create a first path connecting all of them. This path can be considered as the **backbone** of the dungeon and guarantees that at least one valid Hamiltonian path exists.

Afterward, additional tunnels are randomly selected between rooms that are not already directly connected. Their purpose is mainly to make the generated dungeon less obvious and to obtain different configurations between executions.

## 2. Dungeon validation algorithm

The validation is managed in `validator.py`.

First, an adjacency list is created in order to represent which rooms are connected together. The program then uses a **Depth-First Search (DFS) with backtracking**, starting from every possible room.

For each current room, the algorithm tries every connected room that has not been visited yet. When every room has been visited exactly once, the obtained route is stored as a valid path. If a route reaches a dead end before visiting every room, the algorithm goes backward and tries another possibility.

Finally, `main.py` generates the dungeon, executes the validator and prints either the possible valid path(s), or the statement that no valid path exists.

## Sample cases

**Valid dungeon**

```text
Rooms:   [0, 1, 2, 3, 4]
Tunnels: [(0,1), (1,2), (2,3), (3,4)]

Possible path:
0 -> 1 -> 2 -> 3 -> 4
```

Every room is visited exactly once, therefore the dungeon is valid.

**Invalid dungeon**

```text
Rooms:   [0, 1, 2, 3]
Tunnels: [(0,1), (0,2), (0,3)]
```

In this configuration, all external rooms depend on room `0`. It is therefore impossible to visit all rooms exactly once in one continuous path, meaning that no valid Hamiltonian path exists.

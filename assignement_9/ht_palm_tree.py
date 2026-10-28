"""Palm tree (DFS) preprocessing for the Hopcroft-Tarjan algorithm.

A DFS turns the block into a palm tree: tree arcs go down from parent to
child and fronds (back arcs) go up to an ancestor.  Vertices are numbered
in DFS order and, for each vertex v,
  * lowpt1(v) is the lowest number reachable from v by tree arcs followed
    by at most one frond (or v itself);
  * lowpt2(v) is the second lowest such number.
The arcs leaving every vertex are then sorted by the Hopcroft-Tarjan cost
  * frond v -> w        : 2 * number(w)
  * tree arc v -> w     : 2 * lowpt1(w), +1 if lowpt2(w) < number(v)
so that following the first arc of each vertex always gives the path that
goes down and comes back to the lowest possible vertex.
"""


class PalmTree:
    """DFS numbering, lowpoints and sorted arcs of a biconnected block."""

    def __init__(self, adjacency):
        """Run the DFS from an arbitrary root and sort all the arcs."""
        self.adjacency = adjacency
        self.number, self.parent = {}, {}
        self.lowpt1, self.lowpt2 = {}, {}
        self.arcs = {vertex: [] for vertex in adjacency}
        self.root = next(iter(adjacency))
        self.parent[self.root] = None
        self._visit(self.root)
        for vertex in adjacency:
            self._sort_arcs(vertex)

    def _visit(self, vertex):
        """Number vertex, orient its edges and compute its lowpoints."""
        own = len(self.number)
        self.number[vertex] = self.lowpt1[vertex] = self.lowpt2[vertex] = own
        for target in self.adjacency[vertex]:
            if target not in self.number:
                self.parent[target] = vertex
                self.arcs[vertex].append(target)
                self._visit(target)
                self._absorb(vertex, self.lowpt1[target],
                             self.lowpt2[target])
            elif (self.number[target] < own
                  and target != self.parent[vertex]):
                self.arcs[vertex].append(target)
                self._absorb(vertex, self.number[target], own)

    def _absorb(self, vertex, low1, low2):
        """Merge the two lowest values of a child (or frond) into vertex."""
        if low1 < self.lowpt1[vertex]:
            self.lowpt2[vertex] = min(self.lowpt1[vertex], low2)
            self.lowpt1[vertex] = low1
        elif low1 == self.lowpt1[vertex]:
            self.lowpt2[vertex] = min(self.lowpt2[vertex], low2)
        else:
            self.lowpt2[vertex] = min(self.lowpt2[vertex], low1)

    def is_tree_arc(self, tail, head):
        """Return True if tail -> head is a tree arc (not a frond)."""
        return self.parent.get(head) == tail

    def _cost(self, tail, head):
        """Return the Hopcroft-Tarjan sorting cost of the arc tail->head."""
        if not self.is_tree_arc(tail, head):
            return 2 * self.number[head]
        if self.lowpt2[head] < self.number[tail]:
            return 2 * self.lowpt1[head] + 1
        return 2 * self.lowpt1[head]

    def _sort_arcs(self, vertex):
        """Sort the arcs leaving vertex by increasing cost."""
        keyed = sorted((self._cost(vertex, head), head)
                       for head in self.arcs[vertex])
        self.arcs[vertex] = [head for _, head in keyed]

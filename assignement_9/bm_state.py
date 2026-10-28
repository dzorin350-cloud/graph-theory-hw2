"""Data structures of the Boyer-Myrvold edge-addition planarity test.

Vertices are renamed by their DFS index (DFI) 0 .. n-1.  For every DFS
child c there is also a virtual root n + c: a copy of parent(c) that is
the root of the biconnected component (bicomp) holding the tree edge
(parent(c), c).  At the start each tree edge is its own bicomp.

Only the external face of each bicomp is stored: link[x] holds the two
neighbours of x on that face.  The test never needs the full embedding,
so a bicomp is walked by leaving a vertex through the link that is not
the one we came from; this makes bicomp flips unnecessary.

Per vertex v we also keep:
  * least_ancestor[v]: lowest DFI joined to v by a back edge;
  * lowpoint[v]: lowest DFI reachable from the subtree of v;
  * separated[v]: DFS children whose bicomp is not yet merged with v,
    sorted by lowpoint (used to tell if v is externally active);
  * back_edges[v]: descendants joined to v by a back edge.
"""


class BoyerMyrvoldState:
    """DFS information and external-face links of the embedding."""

    def __init__(self, adjacency):
        """Number the vertices by DFS and build the initial bicomps."""
        self.adjacency = adjacency
        self.number, self.vertex_of, self.parent = {}, [], []
        for vertex in adjacency:
            if vertex not in self.number:
                self._number(vertex, None)
        self.size = len(self.vertex_of)
        self._compute_relations()
        self._compute_lowpoints()
        self._build_bicomps()
        self.current = None

    def _number(self, vertex, parent):
        """Recursive DFS assigning the DFS index of every vertex."""
        self.number[vertex] = len(self.vertex_of)
        self.vertex_of.append(vertex)
        self.parent.append(parent)
        for neighbour in self.adjacency[vertex]:
            if neighbour not in self.number:
                self._number(neighbour, self.number[vertex])

    def _compute_relations(self):
        """Fill children, back_edges and least_ancestor for every vertex."""
        self.children = [[] for _ in range(self.size)]
        self.back_edges = [[] for _ in range(self.size)]
        self.least_ancestor = list(range(self.size))
        for index in range(self.size):
            if self.parent[index] is not None:
                self.children[self.parent[index]].append(index)
            for neighbour in self.adjacency[self.vertex_of[index]]:
                other = self.number[neighbour]
                if other < index and other != self.parent[index]:
                    self.back_edges[other].append(index)
                    self.least_ancestor[index] = min(
                        self.least_ancestor[index], other)

    def _compute_lowpoints(self):
        """Compute lowpoints bottom-up and the sorted separated lists."""
        self.lowpoint = list(self.least_ancestor)
        for index in reversed(range(self.size)):
            for child in self.children[index]:
                self.lowpoint[index] = min(self.lowpoint[index],
                                           self.lowpoint[child])
        self.separated = [
            sorted(self.children[index], key=self.lowpoint.__getitem__)
            for index in range(self.size)]

    def _build_bicomps(self):
        """Make every tree edge a bicomp: virtual root n + c and child c."""
        self.link = [[None, None] for _ in range(2 * self.size)]
        for child in range(self.size):
            if self.parent[child] is not None:
                self.link[self.size + child] = [child, child]
                self.link[child] = [self.size + child, self.size + child]
        self.pertinent_roots = [[] for _ in range(self.size)]
        self.backedge_flag = [None] * self.size
        self.visited = [None] * (2 * self.size)

    def step(self, node, in_side):
        """Leave node by the link opposite to in_side.

        Return the next node and the side through which it is entered.
        A 2-vertex bicomp has both links equal, so the side is then
        deduced from the side we left by.
        """
        out_side = 1 - in_side
        target = self.link[node][out_side]
        if self.link[target][0] == self.link[target][1]:
            return target, 1 - out_side
        return target, 0 if self.link[target][0] == node else 1

    def is_root(self, node):
        """Return True if node is a virtual root (a copy of a parent)."""
        return node >= self.size

    def merge(self, parent, parent_in, root, root_out):
        """Merge the bicomp of root into parent along the walked path."""
        other, other_in = self.step(root, root_out)
        self.link[parent][parent_in] = other
        self.link[other][other_in] = parent
        self.pertinent_roots[parent].remove(root)
        self.separated[parent].remove(root - self.size)

    def embed_back_edge(self, root, root_side, vertex, vertex_in):
        """Add the back edge root-vertex on the external face."""
        self.link[root][root_side] = vertex
        self.link[vertex][vertex_in] = root
        self.backedge_flag[vertex] = None

"""Biconnected components (blocks) using Tarjan's DFS lowpoint method.

A graph is planar if and only if each of its blocks is planar, and the
DMP algorithm needs a biconnected input, so the graph is split first.
Each block is returned as a list of edges (u, v).
"""


class BlockFinder:
    """Tarjan's edge-stack algorithm for biconnected components."""

    def __init__(self, adjacency):
        """Prepare the DFS state for the given graph."""
        self.adjacency = adjacency
        self.order = {}
        self.low = {}
        self.edge_stack = []
        self.blocks = []

    def run(self):
        """Visit every connected component and return the blocks."""
        for vertex in self.adjacency:
            if vertex not in self.order:
                self._visit(vertex, None)
        return self.blocks

    def _visit(self, vertex, parent):
        """DFS that closes a block whenever a child cannot climb higher."""
        self.order[vertex] = self.low[vertex] = len(self.order)
        for neighbour in self.adjacency[vertex]:
            if neighbour == parent:
                continue
            if neighbour not in self.order:
                self.edge_stack.append((vertex, neighbour))
                self._visit(neighbour, vertex)
                self.low[vertex] = min(self.low[vertex], self.low[neighbour])
                if self.low[neighbour] >= self.order[vertex]:
                    self._pop_block((vertex, neighbour))
            elif self.order[neighbour] < self.order[vertex]:
                self.edge_stack.append((vertex, neighbour))
                self.low[vertex] = min(self.low[vertex],
                                       self.order[neighbour])

    def _pop_block(self, last_edge):
        """Pop edges down to last_edge; they form one block."""
        block = []
        while True:
            edge = self.edge_stack.pop()
            block.append(edge)
            if edge == last_edge:
                break
        self.blocks.append(block)


def biconnected_components(adjacency):
    """Return the blocks of the graph as lists of edges."""
    return BlockFinder(adjacency).run()

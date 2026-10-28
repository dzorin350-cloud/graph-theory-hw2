"""Hopcroft-Tarjan path-addition planarity test (1974).

The graph is split into biconnected blocks; each block is planar or not
independently.  On a block, after the palm-tree preprocessing:
  1. Starting from an arc, follow the first arc of every vertex: this
     gives a path (the spine) that goes down the tree and closes with a
     frond back to a low vertex w0.  Spine + tree path forms a cycle.
  2. Walk the spine upwards.  Every other arc leaving a spine vertex
     starts a segment; a frond is a segment by itself, a tree arc is
     tested recursively in the same way and returns its attachments.
  3. Two segments interlace when they cannot be on the same side of the
     cycle.  Segments are grouped in blocks on a stack; a new segment is
     placed on the left, flipping/merging the blocks it interlaces.  If
     it interlaces on both sides, the block is not planar.
This is the formulation of K. Mehlhorn (LEDA); it runs in O(V + E).
"""

from collections import deque

from biconnected import biconnected_components
from graph_io import adjacency_from_edges, exceeds_euler_bound
from ht_block import Block
from ht_palm_tree import PalmTree


class HopcroftTarjanTester:
    """Recursive segment test on the palm tree of one block."""

    def __init__(self, adjacency):
        """Build the palm tree of a biconnected block."""
        self.palm = PalmTree(adjacency)

    def is_planar(self):
        """Test the whole block, i.e. the segment of the root's tree arc."""
        if len(self.palm.number) < 3:
            return True
        root = self.palm.root
        child = self.palm.arcs[root][0]
        return self._strongly_planar(root, child) is not None

    def _strongly_planar(self, tail, head):
        """Test the segment of tail->head; return its attachments or None.

        The attachments are the DFS numbers of the vertices below tail
        where the segment comes back, sorted in decreasing order.
        """
        spine_end, low = self._follow_spine(head)
        stack = []
        vertex = spine_end
        while vertex != tail:
            for target in self.palm.arcs[vertex][1:]:
                if not self._add_segment(vertex, target, stack):
                    return None
            parent_number = self.palm.number[self.palm.parent[vertex]]
            while stack and stack[-1].clean(parent_number):
                stack.pop()
            vertex = self.palm.parent[vertex]
        return self._collect(stack, low, tail)

    def _follow_spine(self, head):
        """Follow first arcs from head; return the last vertex and w0."""
        vertex = head
        target = self.palm.arcs[vertex][0]
        while self.palm.is_tree_arc(vertex, target):
            vertex = target
            target = self.palm.arcs[vertex][0]
        return vertex, self.palm.number[target]

    def _add_segment(self, vertex, target, stack):
        """Place the segment of vertex->target; False if impossible."""
        if self.palm.is_tree_arc(vertex, target):
            attachments = self._strongly_planar(vertex, target)
            if attachments is None:
                return False
        else:
            attachments = deque([self.palm.number[target]])
        block = Block(attachments)
        while True:
            if block.left_interlace(stack):
                stack[-1].flip()
            if block.left_interlace(stack):
                return False
            if not block.right_interlace(stack):
                break
            block.combine(stack.pop())
        stack.append(block)
        return True

    def _collect(self, stack, low, tail):
        """Gather the remaining blocks into the segment's attachments."""
        attachments = deque()
        while stack:
            block = stack.pop()
            if (block.left and block.right
                    and block.left[0] > low and block.right[0] > low):
                return None
            block.add_to(attachments, low)
        if low != self.palm.number[tail]:
            attachments.append(low)
        return attachments


def hopcroft_tarjan_is_planar(adjacency):
    """Return True if every biconnected block passes Hopcroft-Tarjan."""
    if exceeds_euler_bound(adjacency):
        return False
    for block in biconnected_components(adjacency):
        tester = HopcroftTarjanTester(adjacency_from_edges(block))
        if not tester.is_planar():
            return False
    return True

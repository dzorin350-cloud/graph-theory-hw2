"""Boyer-Myrvold edge-addition planarity test (2004).

The vertices are processed in decreasing DFS index.  Each tree edge
starts as its own biconnected component (bicomp).  For the current
vertex v:
  1. Walkup: for every back edge (w, v) climb from w and mark the bicomp
     roots on the way as pertinent.
  2. Walkdown: from each virtual root of v, go around the external face
     in both directions.  Back edges to v are embedded as soon as they
     are reached, merging the child bicomps crossed on the way.  The walk
     descends into pertinent child bicomps, skips inactive vertices and
     stops at an externally active vertex, which must stay outside.
  3. If a back edge to v could not be embedded, the graph is not planar.
Total running time is linear in theory (with short-circuit edges);
this simpler version may be quadratic on some inputs.
"""

from bm_state import BoyerMyrvoldState
from bm_walkup import (is_inactive, is_internally_active, is_pertinent,
                       walkup)
from graph_io import exceeds_euler_bound


class BoyerMyrvoldTester:
    """Runs Walkup and Walkdown for every vertex of the graph."""

    def __init__(self, adjacency):
        """Prepare the DFS state and the merge stack."""
        self.state = BoyerMyrvoldState(adjacency)
        self.stack = []

    def is_planar(self):
        """Process vertices by decreasing DFI; False on a failed edge."""
        state = self.state
        for vertex in reversed(range(state.size)):
            state.current = vertex
            for descendant in state.back_edges[vertex]:
                walkup(state, descendant)
            for child in state.children[vertex]:
                self._walkdown(state.size + child)
            if any(state.backedge_flag[descendant] == vertex
                   for descendant in state.back_edges[vertex]):
                return False
        return True

    def _walkdown(self, root):
        """Embed back edges reachable from root, one direction at a time."""
        for side in (0, 1):
            self.stack = []
            if not self._walk_side(root, side):
                return

    def _walk_side(self, root, side):
        """Walk the external face from root; False if blocked midway."""
        state = self.state
        node, node_in = state.step(root, 1 - side)
        while node != root:
            if state.backedge_flag[node] == state.current:
                self._merge_stack()
                state.embed_back_edge(root, side, node, node_in)
            if state.pertinent_roots[node]:
                node, node_in = self._descend(node, node_in)
            elif is_inactive(state, node):
                node, node_in = state.step(node, node_in)
            else:
                break
        return not self.stack

    def _descend(self, node, node_in):
        """Descend into a pertinent child bicomp, internal side first.

        Externally active vertices are thus kept on the external face.
        """
        state = self.state
        self.stack.append((node, node_in))
        root = state.pertinent_roots[node][0]
        x_node, x_in = self._first_active(root, 1)
        y_node, y_in = self._first_active(root, 0)
        if is_internally_active(state, x_node):
            choice = (x_node, x_in, 0)
        elif is_internally_active(state, y_node):
            choice = (y_node, y_in, 1)
        elif is_pertinent(state, x_node):
            choice = (x_node, x_in, 0)
        else:
            choice = (y_node, y_in, 1)
        self.stack.append((root, choice[2]))
        return choice[0], choice[1]

    def _first_active(self, root, in_side):
        """From root, skip inactive vertices; return the first other one.

        This replaces the short-circuit edges of the original paper.
        """
        node, node_in = self.state.step(root, in_side)
        while node != root and is_inactive(self.state, node):
            node, node_in = self.state.step(node, node_in)
        return node, node_in

    def _merge_stack(self):
        """Merge every bicomp crossed since the last embedded edge."""
        while self.stack:
            root, root_out = self.stack.pop()
            parent, parent_in = self.stack.pop()
            self.state.merge(parent, parent_in, root, root_out)


def boyer_myrvold_is_planar(adjacency):
    """Return True if the graph is planar (Boyer-Myrvold)."""
    if exceeds_euler_bound(adjacency):
        return False
    return BoyerMyrvoldTester(adjacency).is_planar()

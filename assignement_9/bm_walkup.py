"""Walkup and vertex activity for the Boyer-Myrvold planarity test.

When vertex v is processed (state.current == v), a vertex w is
  * pertinent if it has a back edge to v still to embed, or a child
    bicomp that leads to such a back edge (a pertinent root);
  * externally active if it, or a separated child subtree, has a back
    edge to an ancestor of v: it must then stay on the external face;
  * internally active if pertinent but not externally active;
  * inactive if neither pertinent nor externally active.
Walkup marks, for one back edge (w, v), every bicomp root met while
climbing from w towards v, so that Walkdown knows where to descend.
"""


def walkup(state, start):
    """Record that start has a back edge to state.current."""
    vertex = state.current
    state.backedge_flag[start] = vertex
    x_node, x_in, y_node, y_in = start, 1, start, 0
    while x_node != vertex:
        if state.visited[x_node] == vertex or state.visited[y_node] == vertex:
            return
        state.visited[x_node] = state.visited[y_node] = vertex
        root = _root_among(state, x_node, y_node)
        if root is None:
            x_node, x_in = state.step(x_node, x_in)
            y_node, y_in = state.step(y_node, y_in)
        else:
            x_node = y_node = _record_root(state, root)
            x_in, y_in = 1, 0


def _root_among(state, x_node, y_node):
    """Return whichever of the two nodes is a virtual root, else None."""
    if state.is_root(x_node):
        return x_node
    if state.is_root(y_node):
        return y_node
    return None


def _record_root(state, root):
    """Add root to its parent's pertinent roots; return the parent.

    Internally active roots go first so Walkdown handles them before the
    externally active ones.
    """
    child = root - state.size
    parent = state.parent[child]
    if parent != state.current:
        if state.lowpoint[child] < state.current:
            state.pertinent_roots[parent].append(root)
        else:
            state.pertinent_roots[parent].insert(0, root)
    return parent


def is_pertinent(state, node):
    """Return True if node still leads to a back edge to the current v."""
    return (state.backedge_flag[node] == state.current
            or bool(state.pertinent_roots[node]))


def is_externally_active(state, node):
    """Return True if node must stay on the external face."""
    if state.least_ancestor[node] < state.current:
        return True
    separated = state.separated[node]
    return bool(separated) and state.lowpoint[separated[0]] < state.current


def is_internally_active(state, node):
    """Return True if node is pertinent but not externally active."""
    return is_pertinent(state, node) and not is_externally_active(state, node)


def is_inactive(state, node):
    """Return True if node can be skipped by Walkdown."""
    return not is_pertinent(state, node) and not is_externally_active(
        state, node)

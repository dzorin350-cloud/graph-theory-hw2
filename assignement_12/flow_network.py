"""Shared tools for the maximum flow programs: reading input and the residual network.

Input file format (one item per line, `#` starts a comment):

    source S
    sink T
    S A 5        # directed edge S -> A with capacity 5
    ...
"""


class FlowNetwork:
    """Directed network stored as a residual graph (edge + reverse edge)."""

    def __init__(self, names, source, sink):
        self.names = names                      # index -> node name
        self.index = {name: i for i, name in enumerate(names)}
        self.source = self.index[source]
        self.sink = self.index[sink]
        self.n = len(names)
        # Each edge is a list [to, residual capacity, index of reverse edge].
        self.graph = [[] for _ in range(self.n)]
        self.original = []                      # (u, v, capacity, position in graph[u])

    def add_edge(self, u, v, capacity):
        forward = [v, capacity, len(self.graph[v])]
        backward = [u, 0, len(self.graph[u])]
        self.graph[u].append(forward)
        self.graph[v].append(backward)
        self.original.append((u, v, capacity, len(self.graph[u]) - 1))

    def push(self, u, edge, amount):
        """Send `amount` along `edge` (leaving u) and update its reverse edge."""
        v, _, rev = edge
        edge[1] -= amount
        self.graph[v][rev][1] += amount

    def edge_flows(self):
        """Return (u, v, flow, capacity) for every edge of the input."""
        result = []
        for u, v, capacity, position in self.original:
            flow = capacity - self.graph[u][position][1]
            result.append((self.names[u], self.names[v], flow, capacity))
        return result

    def min_cut(self):
        """Nodes reachable from the source in the residual graph (set P of the cut)."""
        seen = [False] * self.n
        seen[self.source] = True
        stack = [self.source]
        while stack:
            u = stack.pop()
            for v, residual, _ in self.graph[u]:
                if residual > 0 and not seen[v]:
                    seen[v] = True
                    stack.append(v)
        side_p = [self.names[i] for i in range(self.n) if seen[i]]
        side_q = [self.names[i] for i in range(self.n) if not seen[i]]
        cut_edges = [(self.names[u], self.names[v], c)
                     for u, v, c, _ in self.original if seen[u] and not seen[v]]
        return side_p, side_q, cut_edges


def read_network(lines):
    """Parse the text format described at the top of this file."""
    source = sink = None
    edges = []
    names = []

    def remember(name):
        if name not in names:
            names.append(name)

    for number, line in enumerate(lines, start=1):
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        if parts[0].lower() in ("source", "sink") and len(parts) == 2:
            if parts[0].lower() == "source":
                source = parts[1]
            else:
                sink = parts[1]
            remember(parts[1])
            continue
        if len(parts) != 3:
            raise ValueError("Line {}: expected 'u v capacity'.".format(number))
        u, v, capacity = parts
        try:
            capacity = int(capacity)
        except ValueError:
            raise ValueError("Line {}: capacity must be an integer.".format(number))
        if capacity < 0:
            raise ValueError("Line {}: capacity cannot be negative.".format(number))
        if u == v:
            raise ValueError("Line {}: self-loops are not allowed.".format(number))
        remember(u)
        remember(v)
        edges.append((u, v, capacity))

    if source is None or sink is None:
        raise ValueError("The input must define a 'source' and a 'sink'.")
    if source == sink:
        raise ValueError("The source and the sink must be different nodes.")
    if not edges:
        raise ValueError("The network has no edges.")

    network = FlowNetwork(names, source, sink)
    for u, v, capacity in edges:
        network.add_edge(network.index[u], network.index[v], capacity)
    return network


def print_result(network, max_flow, algorithm):
    """Print the maximum flow, the flow on each edge and a minimum cut."""
    print("\n=== {} ===".format(algorithm))
    print("Source: {}   Sink: {}".format(network.names[network.source],
                                         network.names[network.sink]))
    print("\nFlow on each edge (flow/capacity):")
    for u, v, flow, capacity in network.edge_flows():
        print("  {:>4} -> {:<4} {:>3}/{}".format(u, v, flow, capacity))

    side_p, side_q, cut_edges = network.min_cut()
    cut_value = sum(c for _, _, c in cut_edges)
    print("\nMinimum cut: P = {{{}}}, P' = {{{}}}".format(", ".join(side_p), ", ".join(side_q)))
    print("  Cut edges: " + ", ".join("{}->{} ({})".format(u, v, c) for u, v, c in cut_edges))
    print("  Cut value: {}".format(cut_value))
    print("\nMaximum flow: {}".format(max_flow))
    if cut_value == max_flow:
        print("Max-Flow Min-Cut check: OK (max flow = min cut = {})".format(max_flow))


def load_from_args(argv, usage):
    """Return (network, show_steps) from the command line, or None on error."""
    show_steps = "--steps" in argv
    filenames = [arg for arg in argv if arg != "--steps"]
    if len(filenames) != 1:
        print(usage)
        return None
    try:
        with open(filenames[0], "r", encoding="utf-8") as file:
            return read_network(file), show_steps
    except (OSError, ValueError) as error:
        print("Input error:", error)
        return None

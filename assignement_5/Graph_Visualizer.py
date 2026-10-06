def read_matrix():
    print("Enter rows with spaces. Empty line = finish.")
    matrix = []
    while True:
        line = input().strip()
        if not line:
            break
        matrix.append([int(x) for x in line.replace(",", " ").split()])
    if not matrix or any(len(r) != len(matrix[0]) for r in matrix):
        raise ValueError("Invalid matrix.")
    return matrix


def adjacency_edges(matrix):
    n = len(matrix)
    if any(len(r) != n for r in matrix):
        raise ValueError("Adjacency matrix must be square.")
    for i in range(n):
        for j in range(n):
            if matrix[i][j] != matrix[j][i]:
                raise ValueError("Adjacency matrix must be symmetric.")
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            if matrix[i][j] != 0:
                edges.append((i, j))
    return n, edges


def incidence_edges(matrix):
    n = len(matrix)
    edges = []
    for col in range(len(matrix[0])):
        vertices = [i for i in range(n) if matrix[i][col] == 1]
        if any(matrix[i][col] not in (0, 1) for i in range(n)):
            raise ValueError("Incidence values must be 0 or 1.")
        if len(vertices) != 2:
            raise ValueError("Each incidence column needs two 1 values.")
        edges.append((vertices[0], vertices[1]))
    return n, edges


def graph_list(n, edges, allowed=None):
    graph = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        if allowed is None or i in allowed:
            graph[u].append((v, i))
            graph[v].append((u, i))
    return graph


def spanning_tree(n, edges):
    graph = graph_list(n, edges)
    visited = set()
    tree = []
    for start in range(n):
        if start in visited:
            continue
        visited.add(start)
        queue = [start]
        while queue:
            u = queue.pop(0)
            for v, edge in graph[u]:
                if v not in visited:
                    visited.add(v)
                    queue.append(v)
                    tree.append(edge)
    return tree


def path_in_tree(n, edges, tree, start, goal):
    graph = graph_list(n, edges, set(tree))
    parent = {start: (None, None)}
    queue = [start]
    while queue:
        u = queue.pop(0)
        for v, edge in graph[u]:
            if v not in parent:
                parent[v] = (u, edge)
                queue.append(v)
    if goal not in parent:
        return []
    path = []
    current = goal
    while current != start:
        current, edge = parent[current]
        path.append(edge)
    return path


def cycle_matrix(n, edges, tree):
    result = []
    for i, (u, v) in enumerate(edges):
        if i in tree:
            continue
        path = path_in_tree(n, edges, tree, u, v)
        if path:
            row = [0] * len(edges)
            row[i] = 1
            for edge in path:
                row[edge] = 1
            result.append(row)
    return result


def cutset_matrix(n, edges, tree):
    result = []
    for removed in tree:
        start = edges[removed][0]
        graph = graph_list(n, edges, set(tree) - {removed})
        side = {start}
        queue = [start]
        while queue:
            u = queue.pop(0)
            for v, _ in graph[u]:
                if v not in side:
                    side.add(v)
                    queue.append(v)
        row = []
        for u, v in edges:
            row.append(1 if (u in side) != (v in side) else 0)
        result.append(row)
    return result


def print_graph(n, edges, tree):
    print("\n--- GRAPH ---")
    for i, (u, v) in enumerate(edges):
        mark = "*" if i in tree else " "
        print(f"{mark} [{u + 1}] ---- e{i + 1} ---- [{v + 1}]")

    print("\n* = spanning tree edge")
    print("\nConnections:")
    graph = graph_list(n, edges)
    for i in range(n):
        text = ", ".join(f"{v + 1}(e{e + 1})" for v, e in graph[i])
        print(f"[{i + 1}] -> {text}")


def print_matrix(title, matrix, edge_count):
    print(f"\n--- {title} ---")
    print("     " + " ".join(f"e{i + 1}" for i in range(edge_count)))
    if not matrix:
        print("(no rows)")
    for i, row in enumerate(matrix, 1):
        print(f"r{i}:  " + "  ".join(str(x) for x in row))


def main():
    print("GRAPH VISUALIZER")
    print("1 - Adjacency matrix")
    print("2 - Incidence matrix")
    choice = input("Choice: ").strip()

    try:
        matrix = read_matrix()
        if choice == "1":
            n, edges = adjacency_edges(matrix)
        elif choice == "2":
            n, edges = incidence_edges(matrix)
        else:
            print("Invalid choice.")
            return

        tree = spanning_tree(n, edges)
        print_graph(n, edges, tree)
        print_matrix("FUNDAMENTAL CYCLE MATRIX",
                     cycle_matrix(n, edges, tree), len(edges))
        print_matrix("FUNDAMENTAL CUT-SET MATRIX",
                     cutset_matrix(n, edges, tree), len(edges))

    except ValueError as error:
        print("Error:", error)


if __name__ == "__main__":
    main()

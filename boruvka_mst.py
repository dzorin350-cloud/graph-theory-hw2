"""
Boruvka's Algorithm for MST
"""

def find(parent, x):
    """Follow the chain of parents up to the root of x's group."""
    while parent[x] != x:
        x = parent[x]
    return x

def union(parent, x, y):
    """Merge two groups. Returns False if x and y are already in the same group"""
    rx, ry = find(parent, x), find(parent, y)
    if rx == ry:
        return False
    parent[rx] = ry
    return True


def boruvka_mst(vertices, edges, verbose=True):
    idx = {v: i for i, v in enumerate(vertices)}
    n = len(vertices)
    parent = list(range(n)) 
    mst_edges = []
    total_weight = 0
    num_components = n
    round_num = 0

    while num_components > 1:
        round_num += 1
        cheapest = [None] * n

        for (u, v, w) in edges:
            ru, rv = find(parent, idx[u]), find(parent, idx[v])
            if ru == rv:
                continue
            if cheapest[ru] is None or w < cheapest[ru][0]:
                cheapest[ru] = (w, u, v)
            if cheapest[rv] is None or w < cheapest[rv][0]:
                cheapest[rv] = (w, u, v)

        added_this_round = []
        for i in range(n):
            if cheapest[i] is not None:
                w, u, v = cheapest[i]
                if union(parent, idx[u], idx[v]):
                    mst_edges.append((u, v, w))
                    total_weight += w
                    num_components -= 1
                    added_this_round.append((u, v, w))

        if verbose:
            print(f"Round {round_num}: added {added_this_round}, components left = {num_components}")
        if not added_this_round:
            print("Graph is disconnected.")
            break

    return mst_edges, total_weight


if __name__ == "__main__":
    vertices = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    edges = [
        ('A', 'B', 7), ('A', 'C', 6), ('A', 'G', 5), ('G', 'C', 10),
        ('G', 'F', 6), ('C', 'B', 5), ('C', 'D', 9), ('C', 'E', 9),
        ('C', 'F', 7), ('B', 'D', 7), ('F', 'E', 5), ('E', 'D', 5),
    ]
    mst, weight = boruvka_mst(vertices, edges)
    print("\nMST edges:", mst)
    print("Total MST weight:", weight)

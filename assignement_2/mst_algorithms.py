import heapq

"""
Minimum Spanning Tree Algorithms: Boruvka's, Kruskal's, and Prim's
Includes edge failure simulation.
"""

# --- Helper functions for Boruvka and Kruskal (Disjoint Set Union) ---
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


# --- 1. Boruvka's Algorithm ---
def boruvka_mst(vertices, edges, verbose=False):
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


# --- 2. Kruskal's Algorithm ---
def kruskal_mst(vertices, edges):
    idx = {v: i for i, v in enumerate(vertices)}
    n = len(vertices)
    parent = list(range(n))
    mst_edges = []
    total_weight = 0
    
    # Sort edges by weight
    sorted_edges = sorted(edges, key=lambda item: item[2])
    
    for u, v, w in sorted_edges:
        if union(parent, idx[u], idx[v]):
            mst_edges.append((u, v, w))
            total_weight += w
            
    return mst_edges, total_weight


# --- 3. Prim's Algorithm ---
def prim_mst(vertices, edges, start_node='A'):
    # Create adjacency list
    adj = {v: [] for v in vertices}
    for u, v, w in edges:
        adj[u].append((w, v))
        adj[v].append((w, u))
        
    mst_edges = []
    visited = set([start_node])
    edges_pool = []
    total_weight = 0
    
    # Initialize priority queue with start node's edges
    for w, neighbor in adj[start_node]:
        heapq.heappush(edges_pool, (w, start_node, neighbor))
        
    while edges_pool and len(visited) < len(vertices):
        w, u, v = heapq.heappop(edges_pool)
        if v not in visited:
            visited.add(v)
            mst_edges.append((u, v, w))
            total_weight += w
            
            for next_w, next_node in adj[v]:
                if next_node not in visited:
                    heapq.heappush(edges_pool, (next_w, v, next_node))
                    
    return mst_edges, total_weight


# --- 4. Simulation of Node/Edge Failure ---
def simulate_failure(vertices, edges, failed_edge):
    print(f"\n--- Simulation: Edge {failed_edge[0]}-{failed_edge[1]} Failed ---")
    
    # Filter out the failed edge
    u_fail, v_fail = failed_edge
    adapted_edges = [
        (u, v, w) for (u, v, w) in edges 
        if not ((u == u_fail and v == v_fail) or (u == v_fail and v == u_fail))
    ]
    
    # Recalculate using Kruskal's algorithm
    mst, weight = kruskal_mst(vertices, adapted_edges)
    print("Adapted MST edges:", mst)
    print("New total MST weight:", weight)


# --- Main Execution Block ---
if __name__ == "__main__":
    # Corrected Graph Data based on assignment image
    vertices = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    edges = [
        ('A', 'B', 7), ('A', 'C', 6), ('A', 'F', 10), ('A', 'G', 5),
        ('B', 'C', 5), ('B', 'D', 7), ('B', 'E', 9),
        ('C', 'E', 7), ('C', 'F', 9),
        ('D', 'E', 5),
        ('E', 'F', 5),
        ('F', 'G', 6)
    ]

    print("--- 1. Boruvka's Algorithm ---")
    b_mst, b_weight = boruvka_mst(vertices, edges)
    print("MST edges:", b_mst)
    print("Total weight:", b_weight, "\n")

    print("--- 2. Kruskal's Algorithm ---")
    k_mst, k_weight = kruskal_mst(vertices, edges)
    print("MST edges:", k_mst)
    print("Total weight:", k_weight, "\n")

    print("--- 3. Prim's Algorithm ---")
    p_mst, p_weight = prim_mst(vertices, edges, start_node='A')
    print("MST edges:", p_mst)
    print("Total weight:", p_weight)

    # Run Failure Simulation (removing edge B-C which is in the optimal MST)
    simulate_failure(vertices, edges, ('B', 'C'))

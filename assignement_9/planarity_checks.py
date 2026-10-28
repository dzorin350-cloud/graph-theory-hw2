import networkx as nx
import planarity 

def check_planarity_hopcroft_tarjan(nodes, edges):
    """
    Checks graph planarity using the Hopcroft-Tarjan (Left-Right) Algorithm.
    NetworkX natively uses the Left-Right planarity test by default.
    """
    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    
    is_planar, embedding = nx.check_planarity(G)
    
    print(f"Hopcroft-Tarjan Planarity Check: {'Planar' if is_planar else 'Non-Planar'}")
    return is_planar

def check_planarity_boyer_myrvold(nodes, edges):
    """
    Checks graph planarity using the Boyer-Myrvold Algorithm.
    The 'planarity' package directly wraps John Boyer's Edge Addition implementation.
    """
    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    
    # The planarity module evaluates Boyer-Myrvold natively on NetworkX graphs
    is_planar = planarity.is_planar(G)
    
    print(f"Boyer-Myrvold Planarity Check: {'Planar' if is_planar else 'Non-Planar'}")
    return is_planar

if __name__ == "__main__":
    # Sample Input 1: Planar Graph (A simple square with one diagonal)
    print("--- Test Case 1: Simple Planar Graph ---")
    planar_nodes = [0, 1, 2, 3]
    planar_edges = [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)]
    check_planarity_hopcroft_tarjan(planar_nodes, planar_edges)
    check_planarity_boyer_myrvold(planar_nodes, planar_edges)

    # Sample Input 2: K5 - Complete Graph on 5 Vertices
    print("\n--- Test Case 2: K5 Graph ---")
    k5_nodes = [0, 1, 2, 3, 4]
    k5_edges = [(0, 1), (0, 2), (0, 3), (0, 4), 
                (1, 2), (1, 3), (1, 4), 
                (2, 3), (2, 4), (3, 4)]
    check_planarity_hopcroft_tarjan(k5_nodes, k5_edges)
    check_planarity_boyer_myrvold(k5_nodes, k5_edges)

    # Sample Input 3: K3,3 - Complete Bipartite Graph on 6 Vertices
    print("\n--- Test Case 3: K3,3 Graph ---")
    k33_nodes = [0, 1, 2, 3, 4, 5]
    k33_edges = [(0, 3), (0, 4), (0, 5), 
                 (1, 3), (1, 4), (1, 5), 
                 (2, 3), (2, 4), (2, 5)]
    check_planarity_hopcroft_tarjan(k33_nodes, k33_edges)
    check_planarity_boyer_myrvold(k33_nodes, k33_edges)

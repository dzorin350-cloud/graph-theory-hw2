def validate_dungeon(num_rooms, tunnels):
    """
    Validates if a dungeon has a Hamiltonian path using DFS Backtracking.
    """
    # 1. Build an adjacency list for the undirected graph
    graph = {i: [] for i in range(num_rooms)}
    for u, v in tunnels:
        graph[u].append(v)
        graph[v].append(u)

    # 2. Recursive Depth-First Search function
    def find_path(current_room, visited, path):
        # Base case: all rooms have been visited exactly once
        if len(visited) == num_rooms:
            return path

        for neighbor in graph[current_room]:
            if neighbor not in visited:
                visited.add(neighbor)
                path.append(neighbor)
                
                result = find_path(neighbor, visited, path)
                if result is not None:
                    return result
                
                # Backtrack if the current path leads to a dead end
                visited.remove(neighbor)
                path.pop()
                
        return None

    # 3. Attempt to find a path starting from each possible room
    for start_room in range(num_rooms):
        result = find_path(start_room, {start_room}, [start_room])
        
        if result is not None:
            print("Success! A valid path was found:")
            print(" -> ".join(str(room) for room in result))
            return True

    print("Failure. No valid path exists in this dungeon.")
    return False

print("\nDungeon validation:")
validate_dungeon(len(rooms), tunnels)

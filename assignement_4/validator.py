def validate_dungeon(rooms, tunnels):
    """
    Validates if the generated dungeon can be cleared by visiting 
    every room exactly once. Returns all possible valid paths.
    """
    num_rooms = len(rooms)
    if num_rooms == 0:
        return []
        
    # Build an adjacency list for the graph
    adj_list = {room: [] for room in rooms}
    for u, v in tunnels:
        adj_list[u].append(v)
        adj_list[v].append(u)
        
    valid_paths = []
    
    def dfs(current_room, visited, path):
        # Base case: all rooms have been visited exactly once
        if len(visited) == num_rooms:
            valid_paths.append(list(path))
            return
            
        # Recursive step: explore unvisited neighbors
        for neighbor in adj_list[current_room]:
            if neighbor not in visited:
                visited.add(neighbor)
                path.append(neighbor)
                
                dfs(neighbor, visited, path)
                
                # Backtrack
                path.pop()
                visited.remove(neighbor)
                
    # Initiate DFS from every possible starting room
    for room in rooms:
        dfs(room, {room}, [room])
        
    return valid_paths

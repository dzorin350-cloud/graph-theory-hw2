import random

def generate_dungeon(num_rooms, num_extra_tunnels):
    """
    Generates a list of rooms and tunnels ensuring at least one valid 
    Hamiltonian path exists to clear the dungeon.
    """
    if num_rooms < 1:
        return [], []
        
    rooms = list(range(num_rooms))
    # Shuffle to create a random guaranteed path (the backbone)
    random.shuffle(rooms)
    
    tunnels = set()
    
    # Create the backbone path
    for i in range(num_rooms - 1):
        u = rooms[i]
        v = rooms[i + 1]
        tunnels.add(tuple(sorted((u, v))))
        
    # Find all possible tunnels that do not exist yet
    possible_tunnels = []
    for i in range(num_rooms):
        for j in range(i + 1, num_rooms):
            t = tuple(sorted((i, j)))
            if t not in tunnels:
                possible_tunnels.append(t)
                
    # Add extra branching tunnels to obscure the main path
    random.shuffle(possible_tunnels)
    tunnels_to_add = min(num_extra_tunnels, len(possible_tunnels))
    
    for i in range(tunnels_to_add):
        tunnels.add(possible_tunnels[i])
        
    # Return sorted rooms and tunnels for readability
    return sorted(list(rooms)), sorted(list(tunnels))

import random

def generate_dungeon(num_rooms, extra_tunnels_count):
    """
    Generates a dungeon with a guaranteed Hamiltonian path and additional random tunnels.
    """
    rooms = list(range(num_rooms))
    tunnels = set()
    
    # 1. Create a hidden Hamiltonian path to ensure the dungeon is valid
    shuffled_rooms = rooms.copy()
    random.shuffle(shuffled_rooms)
    
    for i in range(num_rooms - 1):
        u = shuffled_rooms[i]
        v = shuffled_rooms[i + 1]
        tunnels.add(tuple(sorted((u, v))))
        
    # 2. Add extra random tunnels to increase complexity
    attempts = 0
    max_attempts = extra_tunnels_count * 10
    added_extras = 0
    
    while added_extras < extra_tunnels_count and attempts < max_attempts:
        u = random.choice(rooms)
        v = random.choice(rooms)
        
        if u != v:
            tunnel = tuple(sorted((u, v)))
            if tunnel not in tunnels:
                tunnels.add(tunnel)
                added_extras += 1
        attempts += 1
        
    return rooms, list(tunnels)

rooms, tunnels = generate_dungeon(5, 4)
print("Generated rooms:", rooms)
print("Generated tunnels:", tunnels)

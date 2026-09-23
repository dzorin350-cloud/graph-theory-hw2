from generator import generate_dungeon
from validator import validate_dungeon

def main():
    # Dungeon configuration
    num_rooms = 5
    extra_tunnels = 3
    
    print("--- Dungeon Generator & Validator ---")
    print(f"Generating dungeon with {num_rooms} rooms and {extra_tunnels} extra tunnels...\n")
    
    # 1. Generate the dungeon
    rooms, tunnels = generate_dungeon(num_rooms, extra_tunnels)
    
    print(f"Rooms: {rooms}")
    print(f"Tunnels: {tunnels}\n")
    
    # 2. Validate the dungeon
    print("Validating generated routes...")
    paths = validate_dungeon(rooms, tunnels)
    
    # 3. Output results
    if not paths:
        print("Result: No valid path exists.")
    else:
        print(f"Result: Success! Found {len(paths)} possible path(s):")
        for path in paths:
            print(f" -> {path}")

if __name__ == "__main__":
    main()

"""Sudoku solver using graph vertex coloring and backtracking.

Each cell is a vertex, and digits 1 to 9 are its possible colors.
"""

import sys


def build_graph():
    """Connect two cells if they share a row, column, or 3x3 box."""
    graph = {}

    for row in range(9):
        for col in range(9):
            neighbors = set()

            for other_row in range(9):
                for other_col in range(9):
                    same_cell = (row, col) == (other_row, other_col)
                    same_row = row == other_row
                    same_col = col == other_col
                    same_box = (row // 3 == other_row // 3 and
                                col // 3 == other_col // 3)

                    if not same_cell and (same_row or same_col or same_box):
                        neighbors.add((other_row, other_col))

            graph[(row, col)] = neighbors

    return graph


def read_grid(lines):
    """Read 9 lines of 9 digits; 0 or . means an empty cell."""
    rows = [line.strip().replace(" ", "") for line in lines if line.strip()]

    if len(rows) != 9:
        raise ValueError("The Sudoku must contain exactly 9 rows.")

    grid = []
    for row in rows:
        if len(row) != 9 or any(char not in "0123456789." for char in row):
            raise ValueError("Each row must contain 9 digits (or dots).")
        grid.append([0 if char == "." else int(char) for char in row])

    return grid


def print_grid(grid):
    """Display a Sudoku grid in the terminal."""
    for row in range(9):
        if row % 3 == 0:
            print("+-------+-------+-------+")

        print("|", end=" ")
        for col in range(9):
            value = grid[row][col]
            print(value if value != 0 else ".", end=" ")
            if col % 3 == 2:
                print("|", end=" ")
        print()

    print("+-------+-------+-------+")


def is_initial_valid(grid, graph):
    """Check that the given digits do not already break Sudoku rules."""
    for (row, col), neighbors in graph.items():
        value = grid[row][col]
        if value == 0:
            continue

        for other_row, other_col in neighbors:
            if grid[other_row][other_col] == value:
                return False

    return True


def possible_colors(grid, graph, row, col):
    """Return the digits not used by adjacent vertices."""
    used = {grid[r][c] for r, c in graph[(row, col)]}
    return [number for number in range(1, 10) if number not in used]


def solve(grid, graph):
    """Color the unfilled vertices using recursive backtracking."""
    best_cell = None
    best_options = None

    # Choose the empty cell with the fewest available colors.
    for row in range(9):
        for col in range(9):
            if grid[row][col] == 0:
                options = possible_colors(grid, graph, row, col)

                if not options:
                    return False

                if best_options is None or len(options) < len(best_options):
                    best_cell = (row, col)
                    best_options = options

    # No empty cells left: the coloring is complete.
    if best_cell is None:
        return True

    row, col = best_cell
    for number in best_options:
        grid[row][col] = number

        if solve(grid, graph):
            return True

        grid[row][col] = 0  # Undo this choice (backtrack).

    return False


def main():
    if len(sys.argv) > 2:
        print("Usage: python sudoku_solver.py [puzzle.txt]")
        return

    try:
        if len(sys.argv) == 2:
            with open(sys.argv[1], "r", encoding="utf-8") as file:
                grid = read_grid(file)
        else:
            print("Enter 9 rows of 9 digits (0 or . for empty cells):")
            lines = [input(f"Row {row + 1}: ") for row in range(9)]
            grid = read_grid(lines)
    except (OSError, ValueError, EOFError) as error:
        print("Input error:", error)
        return

    graph = build_graph()
    print("\nInitial Sudoku:")
    print_grid(grid)

    if not is_initial_valid(grid, graph):
        print("Invalid Sudoku: some given numbers are in conflict.")
    elif solve(grid, graph):
        print("\nSolution:")
        print_grid(grid)
    else:
        print("No solution exists for this Sudoku.")


if __name__ == "__main__":
    main()

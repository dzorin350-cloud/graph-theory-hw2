"""Assignment problem with the Hungarian (Kuhn-Munkres) algorithm.

A team is assigned to at most one site, and a site to at most one team.
The algorithm minimizes the total distance (or cost).
"""

import sys


def read_problem(lines):
    """Read the number of rows/columns followed by the cost matrix."""
    clean = []
    for line in lines:
        line = line.split("#", 1)[0].strip()
        if line:
            clean.append(line)

    if not clean:
        raise ValueError("The input is empty.")

    try:
        size = [int(x) for x in clean[0].split()]
    except ValueError:
        raise ValueError("The first line must contain two integers: n m.")

    if len(size) != 2 or min(size) <= 0:
        raise ValueError("The first line must contain positive sizes: n m.")

    n, m = size
    if len(clean) != n + 1:
        raise ValueError("Expected exactly {} rows of costs.".format(n))

    costs = []
    for i, line in enumerate(clean[1:]):
        try:
            row = [int(x) for x in line.split()]
        except ValueError:
            raise ValueError("Row {} contains a non-integer value.".format(i + 1))
        if len(row) != m:
            raise ValueError("Row {} must contain {} costs.".format(i + 1, m))
        if any(value < 0 for value in row):
            raise ValueError("Costs cannot be negative.")
        costs.append(row)

    return costs


def show_matrix(matrix, title):
    """Print a matrix with columns aligned in the terminal."""
    print("\n" + title)
    for row in matrix:
        print("  " + " ".join("{:>4}".format(value) for value in row))


def find_zero_matching(matrix):
    """Find the maximum number of row/column pairs with value zero."""
    n = len(matrix)
    matched_row_for_col = [-1] * n

    def try_row(row, visited):
        for col in range(n):
            if matrix[row][col] == 0 and not visited[col]:
                visited[col] = True
                previous_row = matched_row_for_col[col]
                if previous_row == -1 or try_row(previous_row, visited):
                    matched_row_for_col[col] = row
                    return True
        return False

    for row in range(n):
        try_row(row, [False] * n)

    matched_col_for_row = [-1] * n
    for col, row in enumerate(matched_row_for_col):
        if row != -1:
            matched_col_for_row[row] = col

    return matched_col_for_row, matched_row_for_col


def cover_zeros(matrix, matching_rows, matching_cols):
    """Find the minimum number of rows/columns covering all zeros.

    Start from unmatched rows and follow alternating paths along zero cells.
    Unvisited rows and visited columns form a minimum line cover.
    """
    n = len(matrix)
    visited_rows = {i for i in range(n) if matching_rows[i] == -1}
    visited_cols = set()
    to_visit = list(visited_rows)

    while to_visit:
        row = to_visit.pop()
        for col in range(n):
            if matrix[row][col] == 0 and col not in visited_cols:
                visited_cols.add(col)
                next_row = matching_cols[col]
                if next_row != -1 and next_row not in visited_rows:
                    visited_rows.add(next_row)
                    to_visit.append(next_row)

    covered_rows = set(range(n)) - visited_rows
    covered_cols = visited_cols
    return covered_rows, covered_cols


def hungarian(costs, show_steps=False):
    """Return the minimum-cost assignment and its total cost.

    The original matrix can be rectangular. Dummy rows or columns with
    zero cost make it square, as required by this version of the algorithm.
    """
    rows = len(costs)
    cols = len(costs[0])
    n = max(rows, cols)

    # Preserve the input matrix: work on a square copy.
    matrix = [row[:] + [0] * (n - cols) for row in costs]
    matrix += [[0] * n for _ in range(n - rows)]

    # 1. Subtract the minimum of each row.
    for row in range(n):
        minimum = min(matrix[row])
        for col in range(n):
            matrix[row][col] -= minimum
    if show_steps:
        show_matrix(matrix, "1. After row reduction:")

    # 2. Subtract the minimum of each column.
    for col in range(n):
        minimum = min(matrix[row][col] for row in range(n))
        for row in range(n):
            matrix[row][col] -= minimum
    if show_steps:
        show_matrix(matrix, "2. After column reduction:")

    iteration = 0
    while True:
        # 3. Choose independent zeros (no two in the same row/column).
        matching_rows, matching_cols = find_zero_matching(matrix)
        matched_count = sum(col != -1 for col in matching_rows)

        if matched_count == n:
            # We have n independent zeros: optimal assignment found.
            assignments = []
            for row in range(rows):
                col = matching_rows[row]
                if col < cols:  # Skip any artificial site.
                    assignments.append((row, col, costs[row][col]))
            total = sum(cost for _, _, cost in assignments)
            return assignments, total

        # 4. Cover zeros with the minimum number of lines.
        covered_rows, covered_cols = cover_zeros(
            matrix, matching_rows, matching_cols
        )

        # 5. Take the smallest uncovered number.
        uncovered = [
            matrix[row][col]
            for row in range(n)
            for col in range(n)
            if row not in covered_rows and col not in covered_cols
        ]
        minimum = min(uncovered)

        # Subtract from uncovered cells and add at intersections of lines.
        for row in range(n):
            for col in range(n):
                row_covered = row in covered_rows
                col_covered = col in covered_cols
                if not row_covered and not col_covered:
                    matrix[row][col] -= minimum
                elif row_covered and col_covered:
                    matrix[row][col] += minimum

        iteration += 1
        if show_steps:
            print("\nAdjustment {}: {} independent zeros, {} cover lines.".format(
                iteration, matched_count, len(covered_rows) + len(covered_cols)
            ))
            print("Smallest uncovered value:", minimum)
            show_matrix(matrix, "Reduced matrix after adjustment:")


def interactive_input():
    """Let the user type a small instance into the terminal."""
    n = input("Number of teams: ")
    m = input("Number of sites: ")
    lines = [n + " " + m]
    print("Enter {} rows, each containing {} costs:".format(n, m))
    for i in range(int(n)):
        lines.append(input("Team {}: ".format(i + 1)))
    return read_problem(lines)


def main():
    arguments = sys.argv[1:]
    show_steps = "--steps" in arguments
    filenames = [arg for arg in arguments if arg != "--steps"]
    if len(filenames) > 1:
        print("Usage: python hungarian_assignment.py [sample.txt] [--steps]")
        return

    try:
        if filenames:
            with open(filenames[0], "r", encoding="utf-8") as file:
                costs = read_problem(file)
        else:
            costs = interactive_input()
    except (OSError, ValueError, EOFError) as error:
        print("Input error:", error)
        return

    rows = len(costs)
    cols = len(costs[0])
    show_matrix(costs, "Original distance matrix (km):")
    print("Teams: {}, Sites: {}".format(rows, cols))

    assignments, total = hungarian(costs, show_steps)
    print("\nOptimal assignments:")
    for row, col, distance in assignments:
        print("  Team {} -> Site {} ({} km)".format(row + 1, col + 1, distance))
    if rows != cols:
        print("(Unused rows or columns correspond to dummy assignments.)")
    print("Minimum total distance: {} km".format(total))


if __name__ == "__main__":
    main()

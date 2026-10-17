"""
Graph Theory Midterm — Task 3: The Knight's Tour
Course: Informatics ITS Graph Theory Class

Find a sequence of knight moves on an N x M chessboard such that the knight
visits every square exactly once (a Hamiltonian path on the knight's graph).

Algorithm: Backtracking DFS with Warnsdorff's heuristic for move ordering
(always try the square with the fewest onward moves first). The heuristic
finds a tour almost instantly on large boards, while backtracking keeps the
search complete, so "path not found" is only printed when no tour exists.

Input:
    <columns> <rows>
    <x> <y>          starting position of the knight (0-indexed column, row)
Output:
    The coordinates visited by the knight, one "x y" pair per line,
    or "path not found".
"""

import sys

MOVES = [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)]


def neighbors(x, y, cols, rows, visited):
    """Unvisited squares reachable from (x, y) with one knight move."""
    result = []
    for dx, dy in MOVES:
        nx, ny = x + dx, y + dy
        if 0 <= nx < cols and 0 <= ny < rows and not visited[ny][nx]:
            result.append((nx, ny))
    return result


def ordered_moves(x, y, cols, rows, visited):
    """Candidate moves sorted by Warnsdorff's rule (fewest onward moves first)."""
    candidates = neighbors(x, y, cols, rows, visited)
    candidates.sort(key=lambda p: len(neighbors(p[0], p[1], cols, rows, visited)))
    return candidates


def knights_tour(cols, rows, start_x, start_y):
    """Return the list of visited coordinates, or None if no tour exists."""
    if not (0 <= start_x < cols and 0 <= start_y < rows):
        return None

    total = cols * rows

    # Colour argument: a knight alternates square colours every move. On a board
    # with an odd number of squares, the majority colour has one extra square,
    # so a tour must start (and end) on it — i.e. on a square where x + y is even.
    if total % 2 == 1 and (start_x + start_y) % 2 == 1:
        return None

    visited = [[False] * cols for _ in range(rows)]
    visited[start_y][start_x] = True
    path = [(start_x, start_y)]

    # Iterative backtracking: each stack frame holds the remaining candidate
    # moves from the square at the same index in `path`.
    stack = [ordered_moves(start_x, start_y, cols, rows, visited)]

    while stack:
        if len(path) == total:
            return path

        candidates = stack[-1]
        if candidates:
            nx, ny = candidates.pop(0)
            visited[ny][nx] = True
            path.append((nx, ny))
            stack.append(ordered_moves(nx, ny, cols, rows, visited))
        else:
            # Dead end: undo the last move and try the next alternative.
            stack.pop()
            x, y = path.pop()
            visited[y][x] = False

    return None


def main():
    data = sys.stdin.read().split()
    if len(data) < 4:
        print("Usage: provide '<columns> <rows>' and '<x> <y>' on stdin")
        return

    cols, rows, start_x, start_y = map(int, data[:4])
    path = knights_tour(cols, rows, start_x, start_y)

    if path is None:
        print("path not found")
        return

    for x, y in path:
        print(x, y)


if __name__ == "__main__":
    main()

"""Two-phase Knight's Tour search.

Phase 1 tries Warnsdorff's greedy rule with several tie-breaking rules
(linear time each). Phase 2 is a complete backtracking search with pruning,
so "no tour" is only answered when no tour exists.
"""

import random

from board import Board


def impossible_start(cols, rows, start):
    """True when a parity argument proves that no tour starts at start.

    Colour: a knight changes colour at every jump, so on a board with an odd
    number of squares a tour starts on the majority colour (col + row even).
    4 x n: on a board 4 squares wide, every jump from an outer line lands on
    an inner line, so a tour must start on an outer line.
    """
    col, row = start
    odd_colour = (cols * rows) % 2 == 1 and (col + row) % 2 == 1
    inner_line = (cols == 4 and col in (1, 2)) or (rows == 4 and row in (1, 2))
    return odd_colour or inner_line


def greedy_rules(attempts=200, seed=0):
    """Tie-breaking rules tried by phase 1, as (order, tie_break, rng).

    First the 8 rotations of the move order with the border-first and the
    centre-first tie-break, then random tie-breaks with a fixed seed, so the
    output is reproducible.
    """
    moves = Board.MOVES
    for tie_break in (1, -1):
        for shift in range(len(moves)):
            yield (moves[shift:] + moves[:shift], tie_break, None)
    rng = random.Random(seed)
    for _ in range(attempts):
        yield (moves, 0, rng)


def finish(board, path):
    """Unvisit every square of path; return path if it is a full tour."""
    for square in path:
        board.unvisit(square)
    return path if len(path) == board.cols * board.rows else None


def warnsdorff(board, start, rule, on_step):
    """One greedy walk from start following rule, without backtracking.

    At each step the knight jumps to the first square of ordered_moves().
    Returns the tour, or None if the knight gets stuck.
    """
    total = board.cols * board.rows
    path = [start]
    board.visit(start)
    while len(path) < total and board.moves(path[-1]):
        square = board.ordered_moves(path[-1], rule)[0]
        board.visit(square)
        path.append(square)
        if on_step:
            on_step("move", path)
    return finish(board, path)


def has_blocked_square(board, current, remaining):
    """True if an unvisited square can no longer fit in the tour.

    A square with 0 unvisited neighbours can only be the last square, reached
    directly from current. A square with 1 unvisited neighbour can be entered
    but not left, so it must be the last square, unless the knight enters it
    now from current. A tour has one last square: at most one such square.
    """
    near = set(board.moves(current))
    forced_ends = 0
    for square, degree in board.degree.items():
        if square in board.visited:
            continue
        if degree == 0 and (square not in near or remaining > 1):
            return True
        if degree == 1 and square not in near:
            forced_ends += 1
    return forced_ends > 1


def is_disconnected(board, current, remaining):
    """True if a BFS from current through unvisited squares misses some."""
    seen = set(board.moves(current))
    queue = list(seen)
    while queue:
        square = queue.pop()
        for neighbour in board.adj[square]:
            if neighbour not in board.visited and neighbour not in seen:
                seen.add(neighbour)
                queue.append(neighbour)
    return len(seen) < remaining


def is_dead_end(board, current, remaining):
    """True if the remaining unvisited squares cannot all be covered."""
    if remaining == 0:
        return False
    return (has_blocked_square(board, current, remaining)
            or is_disconnected(board, current, remaining))


def advance(board, path, stack, rule):
    """Jump to the next candidate of stack[-1] and push its own candidates.

    A square that leads to a dead end (see is_dead_end) gets no candidates,
    so the search backtracks from it at once.
    """
    path.append(stack[-1].pop(0))
    board.visit(path[-1])
    remaining = board.cols * board.rows - len(path)
    dead = is_dead_end(board, path[-1], remaining)
    stack.append([] if dead else board.ordered_moves(path[-1], rule))


def backtracking(board, start, on_step):
    """Complete DFS from start, candidates in Warnsdorff order.

    stack[i] holds the moves still to try from path[i].
    Returns the tour, or None if no tour exists.
    """
    total, rule = board.cols * board.rows, (Board.MOVES, 1, None)
    board.visit(start)
    path, stack = [start], [board.ordered_moves(start, rule)]
    while stack and len(path) < total:
        event = "move" if stack[-1] else "back"
        if stack[-1]:
            advance(board, path, stack, rule)
        else:
            stack.pop()
            board.unvisit(path.pop())
        if on_step and path:
            on_step(event, path)
    return finish(board, path)


def knights_tour(cols, rows, start, on_step=None):
    """Return the squares visited by a knight's tour from start, or None.

    on_step(event, path) is called after every move ("move"), undo ("back")
    and failed greedy attempt ("restart"), for the simulator.
    """
    col, row = start
    if not (0 <= col < cols and 0 <= row < rows):
        return None
    if impossible_start(cols, rows, start):
        return None
    board = Board(cols, rows)
    for rule in greedy_rules():
        path = warnsdorff(board, start, rule, on_step)
        if path:
            return path
        if on_step:
            on_step("restart", [start])
    return backtracking(board, start, on_step)

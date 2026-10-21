"""
Graph Theory Midterm — Task 3: The Knight's Tour
Course: Informatics ITS Graph Theory Class

Find a sequence of knight moves on an N x M chessboard such that the knight
visits every square exactly once (a Hamiltonian path on the knight's graph).

Files:
    board.py     knight's graph, degrees and Warnsdorff ordering
    search.py    phase 1 (Warnsdorff attempts), phase 2 (backtracking)
    display.py   text board and terminal simulator

Input:
    <columns> <rows>
    <x> <y>          starting position of the knight (0-indexed column, row)
Output:
    The coordinates visited by the knight, one "x y" pair per line,
    or "path not found".

Options:
    --board            also print the final board with the move numbers
    --simulate         animate the search step by step (moves and backtracks)
    --delay SECONDS    pause between two animation frames (default 0.15)
"""

import sys

from display import Simulator, render_board
from search import knights_tour


def parse_options(args):
    """Read the command-line flags, return (simulate, show_board, delay)."""
    delay = 0.15
    if "--delay" in args:
        delay = float(args[args.index("--delay") + 1])
    simulate = "--simulate" in args
    return simulate, simulate or "--board" in args, delay


def print_result(cols, rows, path, show_board):
    """Print the tour as one "x y" line per square, or "path not found".

    With show_board, the numbered board is printed after the coordinates.
    """
    if path is None:
        print("path not found")
        return
    for col, row in path:
        print(col, row)
    if show_board:
        print()
        print(render_board(cols, rows, path, show_knight=False))


def main():
    """Read the board size and the start on stdin, solve, print the tour."""
    simulate, show_board, delay = parse_options(sys.argv[1:])
    data = sys.stdin.read().split()
    if len(data) < 4:
        print("Usage: provide '<columns> <rows>' and '<x> <y>' on stdin")
        return
    cols, rows, start_col, start_row = map(int, data[:4])
    on_step = Simulator(cols, rows, delay) if simulate else None
    path = knights_tour(cols, rows, (start_col, start_row), on_step)
    print_result(cols, rows, path, show_board)


if __name__ == "__main__":
    main()

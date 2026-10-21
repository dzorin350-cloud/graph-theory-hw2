"""Text drawing of the chessboard and step-by-step terminal simulator."""

import time


def cell_text(square, order, knight, width):
    """Text of one square: N for the knight, its move number, or a dot."""
    if square == knight:
        return "N".rjust(width)
    if square in order:
        return str(order[square]).rjust(width)
    return ".".rjust(width)


def render_board(cols, rows, path, show_knight=True):
    """Draw the board as text.

    Each visited square shows its move number; when show_knight is set, the
    last square of path (the knight) shows N.
    """
    order = {square: index + 1 for index, square in enumerate(path)}
    knight = path[-1] if show_knight and path else None
    width = max(2, len(str(cols * rows)))
    border = "+" + ("-" * (width + 2) + "+") * cols
    lines = [border]
    for row in range(rows):
        cells = [cell_text((col, row), order, knight, width)
                 for col in range(cols)]
        lines.append("| " + " | ".join(cells) + " |")
        lines.append(border)
    return "\n".join(lines)


class Simulator:
    """on_step callback that redraws the board after every search event."""

    MESSAGES = {
        "back": "Dead end -> backtracking",
        "restart": "Greedy attempt stuck -> restart with another tie-break",
    }

    def __init__(self, cols, rows, delay):
        """Store the board size and the pause between two frames."""
        self.cols, self.rows, self.delay = cols, rows, delay
        self.counters = {"move": 0, "back": 0, "restart": 0}

    def status(self, path):
        """One-line summary: visited squares, moves, backtracks, restarts."""
        return (f"Knight's Tour {self.cols}x{self.rows}"
                f" | visited {len(path)}/{self.cols * self.rows}"
                f" | moves {self.counters['move']}"
                f" | backtracks {self.counters['back']}"
                f" | restarts {self.counters['restart']}")

    def __call__(self, event, path):
        """Count the event, clear the terminal and draw the new frame."""
        self.counters[event] += 1
        jump = f"Knight jumps to {path[-1][0]} {path[-1][1]}"
        print("\033[H\033[J", end="")
        print(self.status(path))
        print(self.MESSAGES.get(event, jump))
        print(render_board(self.cols, self.rows, path))
        time.sleep(self.delay)

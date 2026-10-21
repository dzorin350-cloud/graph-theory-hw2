"""Knight's graph of a chessboard, with the visited squares and the degrees."""


class Board:
    """Knight's graph of a cols x rows board.

    Every square (col, row) is a vertex; an edge joins two squares one knight
    jump apart. degree[square] is the number of unvisited neighbours.
    """

    MOVES = ((2, 1), (1, 2), (-1, 2), (-2, 1),
             (-2, -1), (-1, -2), (1, -2), (2, -1))

    def __init__(self, cols, rows):
        """Build the adjacency lists and set every degree, nothing visited."""
        self.cols, self.rows = cols, rows
        self.adj = {}
        for row in range(rows):
            for col in range(cols):
                self.adj[(col, row)] = self.jumps((col, row), Board.MOVES)
        self.visited = set()
        self.degree = {square: len(nbrs) for square, nbrs in self.adj.items()}

    def jumps(self, square, order):
        """Squares of the board one knight jump away, in the given order."""
        col, row = square
        return [(col + move_col, row + move_row)
                for move_col, move_row in order
                if 0 <= col + move_col < self.cols
                and 0 <= row + move_row < self.rows]

    def visit(self, square):
        """Mark square visited: each of its neighbours loses one exit."""
        self.visited.add(square)
        for neighbour in self.adj[square]:
            self.degree[neighbour] -= 1

    def unvisit(self, square):
        """Undo visit(square): each of its neighbours gets its exit back."""
        self.visited.discard(square)
        for neighbour in self.adj[square]:
            self.degree[neighbour] += 1

    def moves(self, square, order=MOVES):
        """Unvisited neighbours of square, listed in the given move order."""
        return [neighbour for neighbour in self.jumps(square, order)
                if neighbour not in self.visited]

    def rank(self, square, tie_break, rng):
        """Warnsdorff sort key of square: fewest onward moves first.

        Ties are broken at random when rng is given, otherwise by the distance
        to the centre: tie_break = 1 prefers the border, -1 the centre and
        0 keeps the move order.
        """
        if rng:
            return (self.degree[square], rng.random())
        center_col, center_row = (self.cols - 1) / 2, (self.rows - 1) / 2
        dist = (square[0] - center_col) ** 2 + (square[1] - center_row) ** 2
        return (self.degree[square], -tie_break * dist)

    def ordered_moves(self, square, rule):
        """Unvisited neighbours of square sorted by Warnsdorff's rule.

        rule = (move order, tie_break, rng), see rank(). The move order
        decides between squares that are still equal after rank().
        """
        order, tie_break, rng = rule
        keyed = [(self.rank(neighbour, tie_break, rng), index, neighbour)
                 for index, neighbour in enumerate(self.moves(square, order))]
        return [neighbour for _, _, neighbour in sorted(keyed)]

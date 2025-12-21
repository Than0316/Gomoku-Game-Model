class Board:
    """
    Represents the Gomoku board and game state.

    This class encapsulates the board configuration, the current player,
    and the core game mechanics required for adversarial search algorithms
    such as Minimax and Monte Carlo Tree Search.

    The game is played on a fixed 6×6 board with a four-in-a-row winning
    condition.
    """

    SIZE = 6
    EMPTY = '-'

    def __init__(self, grid=None, player='X'):
        """
        Initialize a board state.

        Parameters
        ----------
        grid : list[list[str]] or None, optional
            A 6×6 matrix representing the board state. Each cell contains
            'X', 'O', or EMPTY. If None, an empty board is created.
        player : {'X', 'O'}, optional
            The player whose turn it is at this board state.
            By convention, player 'X' moves first.
        """
        self.player = player
        self.grid = grid if grid else [
            [self.EMPTY for _ in range(self.SIZE)]
            for _ in range(self.SIZE)
        ]

    def copy(self):
        """
        Create an independent copy of the board.

        This method is used to simulate moves without modifying the
        original board state, which is essential for tree-based
        search algorithms.

        Returns
        -------
        Board
            A deep copy of the current board, including the grid and
            the current player.
        """
        return Board(grid=[row[:] for row in self.grid], player=self.player)

    def legal_moves(self):
        """
        Generate legal moves for the current board state.

        Legal moves are restricted to empty cells that are adjacent
        (including diagonals) to at least one already placed stone.
        This heuristic significantly reduces the branching factor
        while preserving strategically relevant moves.

        If the board is empty, the center position is returned as the
        only legal opening move.

        Returns
        -------
        list[tuple[int, int]]
            A list of (row, column) coordinates representing legal moves.
        """
        moves = []
        is_empty_board = True

        for r in range(self.SIZE):
            for c in range(self.SIZE):
                if self.grid[r][c] == self.EMPTY:
                    has_neighbor = False
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < self.SIZE and 0 <= nc < self.SIZE:
                                if self.grid[nr][nc] != self.EMPTY:
                                    has_neighbor = True
                                    is_empty_board = False
                                    break
                        if has_neighbor:
                            break

                    if has_neighbor:
                        moves.append((r, c))
                else:
                    is_empty_board = False

        if is_empty_board:
            center = self.SIZE // 2 - 1
            return [(center, center)]

        return moves

    def play(self, move):
        """
        Apply a move and return the resulting board state.

        The move is applied immutably: a new board is returned,
        leaving the current board unchanged.

        Parameters
        ----------
        move : tuple[int, int]
            The (row, column) position where the current player
            places a stone.

        Returns
        -------
        Board
            A new board state after the move is applied.

        Raises
        ------
        ValueError
            If the specified cell is already occupied.
        """
        r, c = move
        if self.grid[r][c] != self.EMPTY:
            raise ValueError(f"Cell {move} is already occupied")

        new_board = self.copy()
        new_board.grid[r][c] = self.player
        new_board.player = 'O' if self.player == 'X' else 'X'
        return new_board

    def is_full(self):
        """
        Check whether the board is completely filled.

        Returns
        -------
        bool
            True if there are no empty cells remaining, False otherwise.
        """
        return all(
            self.grid[r][c] != self.EMPTY
            for r in range(self.SIZE)
            for c in range(self.SIZE)
        )

    def print_board(self):
        """
        Print the board state to the terminal.

        This method is intended for human interaction during
        gameplay and debugging.
        """
        print('  ' + ''.join(str(i + 1) for i in range(self.SIZE)))
        for i, row in enumerate(self.grid):
            print(f"{i + 1} " + ''.join(row))

    def check_winner(self, stone):
        """
        Determine whether a given player has won the game.

        A win is defined as four consecutive stones aligned
        horizontally, vertically, or diagonally.

        Parameters
        ----------
        stone : {'X', 'O'}
            The player symbol to check for a winning condition.

        Returns
        -------
        bool
            True if the specified player has achieved four in a row,
            False otherwise.
        """
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

        for r in range(self.SIZE):
            for c in range(self.SIZE):
                if self.grid[r][c] != stone:
                    continue
                for dr, dc in directions:
                    count = 1
                    nr, nc = r + dr, c + dc
                    while (
                        0 <= nr < self.SIZE
                        and 0 <= nc < self.SIZE
                        and self.grid[nr][nc] == stone
                    ):
                        count += 1
                        if count == 4:
                            return True
                        nr += dr
                        nc += dc
        return False
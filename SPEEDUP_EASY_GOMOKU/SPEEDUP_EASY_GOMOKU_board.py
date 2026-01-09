# Converted EASY_GOMOKU Board to use MCTS-style numeric flat representation.
# - states: dict {index: player_int} where player_int is 1 (X) or 2 (O)
# - availables: list of free indices
# - current_player: 1 or 2
# - play(move) accepts flat index and returns a new Board (immutable)
# Keeps the same logic (adjacency legal-move heuristic, 4-in-row win),
# but all moves/players are numeric to match the MCTS representation.

class Board:
    """
    Gomoku board using MCTS-style representation while preserving EASY_GOMOKU logic.

    Representation:
      SIZE (int): board width/height (6)
      N_IN_ROW (int): required in-row to win (4)
      states (dict): mapping index -> player (1 or 2)
      availables (list): list of available indices
      current_player (int): 1 or 2 (1 maps to 'X', 2 maps to 'O')
      last_move (int): last move index or -1
    """

    SIZE = 6
    N_IN_ROW = 4
    EMPTY = 0
    PLAYER_CHAR = {1: 'X', 2: 'O'}

    def __init__(self, states=None, current_player=1):
        # states: dict mapping index -> player_int (1 or 2)
        self.current_player = current_player
        self.states = dict(states) if states else {}
        self.availables = [i for i in range(self.SIZE * self.SIZE) if i not in self.states]
        self.last_move = -1 if not self.states else max(self.states.keys())

    def copy(self):
        return Board(states=self.states.copy(), current_player=self.current_player)

    def _idx_to_rc(self, idx):
        return divmod(idx, self.SIZE)

    def _rc_to_idx(self, r, c):
        return r * self.SIZE + c

    def legal_moves(self):
        """
        Generate legal moves using the same adjacency heuristic as the original EASY_GOMOKU:
        - If board is empty return the center
        - Otherwise return indices of empty cells that have at least one neighbor stone
          in 8-neighborhood.
        Returns:
            list[int] of flat indices
        """
        moves = []
        is_empty_board = len(self.states) == 0

        for r in range(self.SIZE):
            for c in range(self.SIZE):
                idx = self._rc_to_idx(r, c)
                if idx in self.states:
                    is_empty_board = False
                    continue

                has_neighbor = False
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.SIZE and 0 <= nc < self.SIZE:
                            nidx = self._rc_to_idx(nr, nc)
                            if nidx in self.states:
                                has_neighbor = True
                                break
                    if has_neighbor:
                        break

                if has_neighbor:
                    moves.append(idx)

        if is_empty_board:
            center = self.SIZE // 2 - 1
            return [self._rc_to_idx(center, center)]

        return moves

    def play(self, move):
        """
        Apply move immutably and return a new Board.

        Parameters
        ----------
        move : int
            Flat index (row * SIZE + col)

        Returns
        -------
        Board
            New board with move applied.

        Raises
        ------
        ValueError
            If the cell is already occupied.
        """
        if move in self.states:
            raise ValueError(f"Cell {move} is already occupied")

        new_board = self.copy()
        new_board.states[move] = self.current_player
        if move in new_board.availables:
            new_board.availables.remove(move)
        new_board.last_move = move
        new_board.current_player = 1 if self.current_player == 2 else 2
        return new_board

    def is_full(self):
        return len(self.availables) == 0

    def print_board(self):
        """
        Print the board in a human-readable format similar to the original file.
        Uses 'X' for player 1, 'O' for player 2, '-' for empty.
        """
        print('  ' + ''.join(str(i + 1) for i in range(self.SIZE)))
        for r in range(self.SIZE):
            row_chars = []
            for c in range(self.SIZE):
                idx = self._rc_to_idx(r, c)
                p = self.states.get(idx, self.EMPTY)
                ch = self.PLAYER_CHAR.get(p, '-')
                row_chars.append(ch)
            print(f"{r + 1} " + ''.join(row_chars))

    def check_winner(self, stone):
        """
        Check if given stone (1 or 2) has N_IN_ROW in a row.
        Returns True/False.
        """
        if isinstance(stone, str):
            # Allow 'X' / 'O' if called with chars; convert to numeric
            inv = {'X': 1, 'O': 2}
            stone = inv.get(stone, stone)

        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

        for r in range(self.SIZE):
            for c in range(self.SIZE):
                idx = self._rc_to_idx(r, c)
                if self.states.get(idx, self.EMPTY) != stone:
                    continue
                for dr, dc in directions:
                    count = 1
                    nr, nc = r + dr, c + dc
                    while (
                        0 <= nr < self.SIZE
                        and 0 <= nc < self.SIZE
                        and self.states.get(self._rc_to_idx(nr, nc), self.EMPTY) == stone
                    ):
                        count += 1
                        if count == self.N_IN_ROW:
                            return True
                        nr += dr
                        nc += dc
        return False
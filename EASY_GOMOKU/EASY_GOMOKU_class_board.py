# board.py

class Board:
    SIZE = 6
    EMPTY = '-'

    def __init__(self, grid=None, player='X'): # "X" goes first
        """
        Grid : board state.
        Player : which player's turn at the current board state.
        """
        self.player = player
        self.grid = grid if grid else [[self.EMPTY for _ in range(self.SIZE)] for _ in range(self.SIZE)]

    def copy(self):
        """
        Return a new Board object that is an independent copy of the current board
        (including its grid and the current player) in order to simulate moves without 
        modifying the original board.
        """
        return Board(grid=[row[:] for row in self.grid], player=self.player)

    def legal_moves(self):
        """
        Empty moves within the board.
        """
        moves = [(r, c) for r in range(self.SIZE) for c in range(self.SIZE) if self.grid[r][c] == self.EMPTY]
        return moves

    def play(self, move):
        """
        Place a stone on a valid position.
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
        Checks whether the board has any empty cells left, and returns a boolean value.
        """
        return all(self.grid[r][c] != self.EMPTY for r in range(self.SIZE) for c in range(self.SIZE))

    def print_board(self):
        print('  ' + ''.join(str(i+1) for i in range(self.SIZE)))
        for i, row in enumerate(self.grid):
            print(f"{i+1} " + ''.join(row))

    def check_winner(self, stone):
        directions = [(1,0),(0,1),(1,1),(1,-1)]
        for r in range(self.SIZE):
            for c in range(self.SIZE):
                if self.grid[r][c] != stone:
                    continue
                for dr, dc in directions:
                    count = 1
                    nr, nc = r + dr, c + dc
                    while 0 <= nr < self.SIZE and 0 <= nc < self.SIZE and self.grid[nr][nc] == stone:
                        count += 1
                        if count == 4:
                            return True
                        nr += dr
                        nc += dc
        return False

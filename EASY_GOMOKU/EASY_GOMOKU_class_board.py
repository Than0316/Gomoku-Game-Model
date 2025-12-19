#run "make html" to update the webpage for documentation
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
        Returns only empty cells that are adjacent to at least one placed stone.
        This focuses the AI on relevant areas of the board.
        """
        moves = []
        is_empty_board = True

        for r in range(self.SIZE):
            for c in range(self.SIZE):
                if self.grid[r][c] == self.EMPTY:
                    # Check 8 neighbors (including diagonals)
                    has_neighbor = False
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = r + dr, c + dc
                            # Check bounds and if neighbor is not empty
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

        # If the board is totally empty, return the center move to start the game
        if is_empty_board:
            center = self.SIZE // 2 - 1
            return [(center, center)]

        return moves

    def play(self, move):
        """
        Place a stone on a valid position.

        Parameters
        ----------
        move

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

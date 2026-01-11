from Gomoku_8_8.GOMOKU_8x8_config import Config

class Board:
    def __init__(self, grid=None, player='X'):
        self.player = player
        self.grid = grid if grid else [[Config.EMPTY for _ in range(Config.SIZE)] for _ in range(Config.SIZE)]

    def copy(self):
        return Board(grid=[row[:] for row in self.grid], player=self.player)

    def legal_moves(self):
        """
        Returns empty spots adjacent to existing stones (Neighborhood Search).
        This drastically speeds up Alpha-Beta pruning on 8x8.
        """
        moves = []
        is_empty_board = True
        
        # Helper to check bounds
        def is_valid(r, c):
            return 0 <= r < Config.SIZE and 0 <= c < Config.SIZE

        for r in range(Config.SIZE):
            for c in range(Config.SIZE):
                if self.grid[r][c] == Config.EMPTY:
                    # Check 8 neighbors
                    has_neighbor = False
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if dr == 0 and dc == 0: continue
                            if is_valid(r + dr, c + dc):
                                if self.grid[r + dr][c + dc] != Config.EMPTY:
                                    has_neighbor = True
                                    is_empty_board = False
                                    break
                        if has_neighbor: break
                    
                    if has_neighbor:
                        moves.append((r, c))
                else:
                    is_empty_board = False
        
        # If board is empty, play center
        if is_empty_board:
            center = Config.SIZE // 2 - 1
            return [(center, center)]
            
        return moves

    def play(self, move):
        r, c = move
        if self.grid[r][c] != Config.EMPTY:
            raise ValueError(f"Cell {move} is occupied")
        new_board = self.copy()
        new_board.grid[r][c] = self.player
        new_board.player = 'O' if self.player == 'X' else 'X'
        return new_board

    def is_full(self):
        return all(self.grid[r][c] != Config.EMPTY for r in range(Config.SIZE) for c in range(Config.SIZE))

    def check_winner(self, stone):
        # 5-in-a-row check
        dirs = [(1,0), (0,1), (1,1), (1,-1)]
        for r in range(Config.SIZE):
            for c in range(Config.SIZE):
                if self.grid[r][c] != stone: continue
                for dr, dc in dirs:
                    # Check if 5 fit
                    if 0 <= r + 4*dr < Config.SIZE and 0 <= c + 4*dc < Config.SIZE:
                        if all(self.grid[r + k*dr][c + k*dc] == stone for k in range(5)):
                            return True
        return False

    def print_board(self):
        print('  ' + ''.join(str(i+1) for i in range(Config.SIZE)))
        for i, row in enumerate(self.grid):
            print(f"{i+1} " + ''.join(row))
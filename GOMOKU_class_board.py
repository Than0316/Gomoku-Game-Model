import time
from GOMOKU_class_shape import ShapeDetector, ShapeType

class Board:
    def __init__(self, size=15, first_role=1):
        self.size = size
        # 0: Empty, 1: Black, -1: White
        self.board = [[0 for _ in range(size)] for _ in range(size)]
        self.first_role = first_role
        self.current_role = first_role
        self.history = []
        
        # Directions: Horizontal, Vertical, Diagonal(\), Diagonal(/)
        self.directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

        # --- Placeholders for advanced modules ---
        # self.zobrist = Zobrist(size) 
        # self.evaluator = Evaluate(size) 
        # self.caches = {} 

    def is_game_over(self):
        """Checks if the game has ended (Win or Draw)."""
        winner = self.get_winner()
        if winner != 0:
            return True, winner
        
        # Check for draw (full board)
        for row in self.board:
            if 0 in row:
                return False, 0
        return True, 0 # Draw

    def get_winner(self):
        """
        Scans the board to see if anyone has 5 in a row.
        Returns 1 (Black), -1 (White), or 0 (None).
        """
        # Optimization: In a real engine, only check the last move.
        # Here we scan all non-empty points for robustness.
        for i in range(self.size):
            for j in range(self.size):
                role = self.board[i][j]
                if role == 0:
                    continue
                
                for dx, dy in self.directions:
                    count = 1
                    # Forward check
                    nx, ny = i + dx, j + dy
                    while 0 <= nx < self.size and 0 <= ny < self.size and self.board[nx][ny] == role:
                        count += 1
                        nx += dx
                        ny += dy
                    
                    if count >= 5:
                        return role
        return 0

    def put(self, row, col, role=None):
        """Places a piece on the board."""
        if role is None:
            role = self.current_role
            
        if not (0 <= row < self.size and 0 <= col < self.size):
            print(f"Invalid move: ({row}, {col}) out of bounds")
            return False
            
        if self.board[row][col] != 0:
            print(f"Invalid move: ({row}, {col}) is occupied")
            return False

        self.board[row][col] = role
        self.history.append({'row': row, 'col': col, 'role': role})
        
        # Update external modules here
        # self.zobrist.toggle_piece(row, col, role)
        # self.evaluator.move(row, col, role)
        
        self.current_role *= -1 # Switch turns
        return True

    def undo(self):
        """Reverts the last move."""
        if not self.history:
            return False
            
        last_move = self.history.pop()
        row, col = last_move['row'], last_move['col']
        self.board[row][col] = 0
        self.current_role = last_move['role'] # Switch back
        
        # Revert external modules here
        # self.zobrist.toggle_piece(row, col, last_move['role'])
        # self.evaluator.undo(row, col)
        return True

    def get_valid_moves(self):
        """Returns a list of all empty coordinates."""
        moves = []
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0:
                    moves.append((i, j))
        return moves

    def get_valuable_moves(self, role, depth=0, only_three=False, only_four=False):
        """
        Generator for heuristic moves.
        In Gomoku, you usually only want to check spots adjacent to existing stones
        (neighbors within 1 or 2 steps).
        """
        # NOTE: In the full AI, this connects to the Evaluator class.
        # Here is a basic implementation that returns neighbors.
        
        if not self.history:
             # If board is empty, return center
            center = self.size // 2
            return [(center, center)]

        valuable_moves = set()
        neighbor_dist = 2 # Look 2 steps around existing stones
        
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] != 0:
                    # Check surrounding empty spots
                    for dx in range(-neighbor_dist, neighbor_dist + 1):
                        for dy in range(-neighbor_dist, neighbor_dist + 1):
                            if dx == 0 and dy == 0: continue
                            
                            ni, nj = i + dx, j + dy
                            if 0 <= ni < self.size and 0 <= nj < self.size:
                                if self.board[ni][nj] == 0:
                                    valuable_moves.add((ni, nj))
        
        return list(valuable_moves)

    def display(self):
        """Prints the board to console."""
        print("   " + " ".join([f"{i:X}" for i in range(self.size)])) # Header 0-F
        for i in range(self.size):
            row_str = f"{i:2d} "
            for j in range(self.size):
                if self.board[i][j] == 0:
                    row_str += "- "
                elif self.board[i][j] == 1:
                    row_str += "● " # Black
                elif self.board[i][j] == -1:
                    row_str += "○ " # White
            print(row_str)
    
    def hash(self):
        """
        [PLACEHOLDER] Generates a hash key for transposition table lookup.
        In a full engine, this would use Zobrist Hashing for speed.
        For now, we use a simple string representation.
        """
        # (Assuming the grid uses 1, -1, 0)
        return tuple(tuple(row) for row in self.board)
from Gomoku_8_8.GOMOKU_8x8_board import Board as MiniBoard
from Gomoku_8_8.GOMOKU_8x8_minimax import find_best_move

class MinimaxPlayer:
    def __init__(self, depth=3):
        self.depth = depth
        self.player = None

    def set_player_ind(self, p):
        self.player = p

    def get_action(self, board):
        # Convert AlphaZero Board (dict) to Minimax Board (2D List)
        grid = [['-' for _ in range(8)] for _ in range(8)]
        for move, p in board.states.items():
            r, c = divmod(move, 8)
            grid[r][c] = 'X' if p == 1 else 'O'
        
        m_board = MiniBoard(grid=grid, player='X' if self.player == 1 else 'O')
        move_tuple = find_best_move(m_board, depth=self.depth)
        return move_tuple[0] * 8 + move_tuple[1]

    def reset_player(self):
        pass

    def __str__(self):
        return f"Minimax (D{self.depth})"
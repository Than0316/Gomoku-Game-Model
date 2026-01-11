import time
from Gomoku_8_8.GOMOKU_8x8_config import Config
from Gomoku_8_8.GOMOKU_8x8_board import Board
from Gomoku_8_8.GOMOKU_8x8_minimax import find_best_move

def get_human_move(board):
    while True:
        try:
            u = input(f"Player {board.player} (row col): ").split()
            if len(u) != 2: continue
            r, c = int(u[0])-1, int(u[1])-1
            if 0 <= r < Config.SIZE and 0 <= c < Config.SIZE and board.grid[r][c] == Config.EMPTY:
                return (r, c)
            print("Invalid move.")
        except ValueError: pass

def main():
    print("=== GOMOKU 8x8 (5-in-a-row) AI ===")
    choice = input("Go first? (y/n): ").lower()
    human = 'X' if choice == 'y' else 'O'
    ai = 'O' if human == 'X' else 'X'
    
    board = Board(player='X')

    while True:
        print("\n----------------")
        board.print_board()
        
        if board.check_winner('X'): print("X Wins!"); break
        if board.check_winner('O'): print("O Wins!"); break
        if board.is_full(): print("Draw!"); break

        if board.player == human:
            move = get_human_move(board)
        else:
            print(f"AI ({ai}) thinking...")
            start = time.time()
            
            depth_to_search = 3
            
            move = find_best_move(board, depth=depth_to_search)
            
            dur = time.time() - start
            print(f"AI played: {move[0]+1} {move[1]+1} (Time: {dur:.2f}s, Depth: {depth_to_search})")
        
        board = board.play(move)

if __name__ == "__main__":
    main()
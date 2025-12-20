import sys
from EASY_GOMOKU_class_board import Board
from EASY_GOMOKU_minimax import find_best_move

def get_human_move(board):
    """
    Prompts the human player for a move and validates it.
    Input is expected as 'row col' (e.g., '3 4').
    """
    while True:
        try:
            user_input = input(f"Player {board.player}, enter move (row col) from 1-6: ").split()
            if len(user_input) != 2:
                print("Invalid format. Please enter two numbers separated by a space.")
                continue
            
            # Convert 1-based input to 0-based index
            r, c = int(user_input[0]) - 1, int(user_input[1]) - 1
            
            if 0 <= r < board.SIZE and 0 <= c < board.SIZE:
                if board.grid[r][c] == board.EMPTY:
                    return (r, c)
                else:
                    print("That cell is already occupied!")
            else:
                print("Out of bounds! Enter numbers between 1 and 6.")
        except ValueError:
            print("Invalid input. Please enter numbers.")

def main():
    print("========================================")
    print("      GOMOKU 4-IN-A-ROW (6x6) AI")
    print("========================================")

    # 1. Setup Turn Order
    choice = input("Do you want to go first? (y/n): ").lower().strip()
    if choice == 'y':
        human_player = 'X'
        ai_player = 'O'
        print("You are 'X'. Computer is 'O'.")
    else:
        human_player = 'O'
        ai_player = 'X'
        print("Computer is 'X'. You are 'O'.")

    # 2. Initialize Empty Board
    # 'X' always starts first according to the Board class logic
    game_board = Board(player='X')
    
    # 3. Game Loop
    while True:
        print("\n-------------------------")
        game_board.print_board()
        
        # Check for Game Over (Win or Draw)
        if game_board.check_winner('X'):
            print("\nGAME OVER: Player 'X' wins!")
            break
        if game_board.check_winner('O'):
            print("\nGAME OVER: Player 'O' wins!")
            break
        if game_board.is_full():
            print("\nGAME OVER: It's a draw!")
            break

        # 4. Turn Handling
        if game_board.player == human_player:
            move = get_human_move(game_board)
        else:
            print(f"\nAI ({ai_player}) is thinking...")
            # Depth 3 is used for a good balance of speed and logic in simple minimax
            move = find_best_move(game_board, depth=4)
            if move:
                print(f"AI plays: Row {move[0]+1}, Col {move[1]+1}")
            else:
                print("AI could not find a move.")
                break

        # 5. Apply move
        game_board = game_board.play(move)

    print("\nGame End:")
    game_board.print_board()
    print("========================================")

if __name__ == "__main__":
    main()
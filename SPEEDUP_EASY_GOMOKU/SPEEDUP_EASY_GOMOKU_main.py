from SPEEDUP_EASY_GOMOKU_board import Board
from SPEEDUP_EASY_GOMOKU_minimax import find_best_move


def get_human_move(board):
    """
    Prompt the human player for a valid move.
    Input: "row col" (1-based)
    Returns: flat index (int)
    """
    while True:
        try:
            user_input = input(
                f"Player {Board.PLAYER_CHAR[board.current_player]}, enter move (row col) from 1-6: "
            ).split()

            if len(user_input) != 2:
                print("Invalid format. Please enter two numbers separated by a space.")
                continue

            # Convert from 1-based input to 0-based indexing
            r, c = int(user_input[0]) - 1, int(user_input[1]) - 1

            if 0 <= r < board.SIZE and 0 <= c < board.SIZE:
                idx = r * board.SIZE + c
                if idx not in board.states:
                    return idx
                else:
                    print("That cell is already occupied!")
            else:
                print("Out of bounds! Enter numbers between 1 and 6.")

        except ValueError:
            print("Invalid input. Please enter numeric values.")


def main():
    """
    Run an interactive Gomoku game using the MCTS-style Board, but the same
    gameplay flow as the original EASY_GOMOKU_main.
    """
    print("========================================")
    print("      GOMOKU 4-IN-A-ROW (6x6) AI")
    print("========================================")

    # 1. Setup turn order
    choice = input("Do you want to go first? (y/n): ").lower().strip()
    if choice == 'y':
        human_player = 1  # 'X'
        ai_player = 2
        print("You are 'X'. Computer is 'O'.")
    else:
        human_player = 2
        ai_player = 1
        print("Computer is 'X'. You are 'O'.")

    # 2. Initialize empty board. current_player 1 (X) starts by convention
    game_board = Board(states=None, current_player=1)

    # 3. Main game loop
    while True:
        print("\n-------------------------")
        game_board.print_board()

        # Check terminal conditions
        if game_board.check_winner(1):
            print("\nGAME OVER: Player 'X' wins!")
            break
        if game_board.check_winner(2):
            print("\nGAME OVER: Player 'O' wins!")
            break
        if game_board.is_full():
            print("\nGAME OVER: It's a draw!")
            break

        # 4. Turn handling
        if game_board.current_player == human_player:
            move = get_human_move(game_board)
        else:
            print(f"\nAI ({Board.PLAYER_CHAR[ai_player]}) is thinking...")
            move = find_best_move(game_board, depth=4)

            if move is not None:
                r = move // game_board.SIZE
                c = move % game_board.SIZE
                print(f"AI plays: Row {r + 1}, Col {c + 1}")
            else:
                print("AI could not find a move.")
                break

        # 5. Apply move (immutably)
        game_board = game_board.play(move)

    print("\nFinal Board State:")
    game_board.print_board()
    print("========================================")


if __name__ == "__main__":
    main()
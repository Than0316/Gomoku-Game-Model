from EASY_GOMOKU_class_board import Board
from EASY_GOMOKU_minimax import find_best_move


def get_human_move(board):
    """
    Prompt the human player for a valid move.

    This function repeatedly requests input from the human player until
    a valid move is provided. Input is expected in the format
    ``row col`` using 1-based indexing.

    Parameters
    ----------
    board : Board
        The current board state.

    Returns
    -------
    tuple[int, int]
        A valid move represented as a (row, column) pair using
        0-based indexing.
    """
    while True:
        try:
            user_input = input(
                f"Player {board.player}, enter move (row col) from 1-6: "
            ).split()

            if len(user_input) != 2:
                print("Invalid format. Please enter two numbers separated by a space.")
                continue

            # Convert from 1-based input to 0-based indexing
            r, c = int(user_input[0]) - 1, int(user_input[1]) - 1

            if 0 <= r < board.SIZE and 0 <= c < board.SIZE:
                if board.grid[r][c] == board.EMPTY:
                    return (r, c)
                else:
                    print("That cell is already occupied!")
            else:
                print("Out of bounds! Enter numbers between 1 and 6.")

        except ValueError:
            print("Invalid input. Please enter numeric values.")


def main():
    """
    Run an interactive Gomoku game in the terminal.

    This function initializes the game, manages turn-taking between the
    human player and the AI, and handles game termination conditions
    (win or draw). The AI selects moves using a depth-limited Minimax
    search.
    """
    print("========================================")
    print("      GOMOKU 4-IN-A-ROW (6x6) AI")
    print("========================================")

    # 1. Setup turn order
    choice = input("Do you want to go first? (y/n): ").lower().strip()
    if choice == 'y':
        human_player = 'X'
        ai_player = 'O'
        print("You are 'X'. Computer is 'O'.")
    else:
        human_player = 'O'
        ai_player = 'X'
        print("Computer is 'X'. You are 'O'.")

    # 2. Initialize empty board
    # By convention, player 'X' always starts first
    game_board = Board(player='X')

    # 3. Main game loop
    while True:
        print("\n-------------------------")
        game_board.print_board()

        # Check terminal conditions
        if game_board.check_winner('X'):
            print("\nGAME OVER: Player 'X' wins!")
            break
        if game_board.check_winner('O'):
            print("\nGAME OVER: Player 'O' wins!")
            break
        if game_board.is_full():
            print("\nGAME OVER: It's a draw!")
            break

        # 4. Turn handling
        if game_board.player == human_player:
            move = get_human_move(game_board)
        else:
            print(f"\nAI ({ai_player}) is thinking...")
            move = find_best_move(game_board, depth=4)

            if move:
                print(f"AI plays: Row {move[0] + 1}, Col {move[1] + 1}")
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

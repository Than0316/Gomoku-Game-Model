###
BOARD_SIZE = 15
EMPTY = "."
PLAYER1 = "X"
PLAYER2 = "O"

def create_board():
    return [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

def print_board(board):
    print("   " + " ".join(f"{i:2}" for i in range(BOARD_SIZE)))
    for i, row in enumerate(board):
        print(f"{i:2} " + " ".join(row))

def check_win(board, symbol):
    # Check horizontal, vertical, and both diagonals
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            # Horizontal
            if j <= BOARD_SIZE - 5 and all(board[i][j+k] == symbol for k in range(5)):
                return True
            # Vertical
            if i <= BOARD_SIZE - 5 and all(board[i+k][j] == symbol for k in range(5)):
                return True
            # Diagonal down-right
            if i <= BOARD_SIZE - 5 and j <= BOARD_SIZE - 5 and all(board[i+k][j+k] == symbol for k in range(5)):
                return True
            # Diagonal up-right
            if i >= 4 and j <= BOARD_SIZE - 5 and all(board[i-k][j+k] == symbol for k in range(5)):
                return True
    return False

def get_move(board, player):
    while True:
        try:
            move = input(f"{player}'s turn. Enter move (row col): ")
            row, col = map(int, move.split())
            if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
                if board[row][col] == EMPTY:
                    return row, col
                else:
                    print("Cell already occupied. Try again.")
            else:
                print("Coordinates out of range. Try again.")
        except ValueError:
            print("Invalid input. Enter two numbers separated by space.")

def main():
    board = create_board()
    print_board(board)
    turn = 0
    while True:
        player = PLAYER1 if turn % 2 == 0 else PLAYER2
        row, col = get_move(board, player)
        board[row][col] = player
        print_board(board)
        if check_win(board, player):
            print(f"{player} wins!")
            break
        turn += 1
        # Optional: detect draw
        if all(board[i][j] != EMPTY for i in range(BOARD_SIZE) for j in range(BOARD_SIZE)):
            print("Draw! No empty cells left.")
            break

if __name__ == "__main__":
    main()

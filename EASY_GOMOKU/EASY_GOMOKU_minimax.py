from EASY_GOMOKU_class_shape import Shape
from EASY_GOMOKU_evaluation_function import evaluate


def minimax(board, depth, is_maximizing, ai_player):
    """
    Perform a depth-limited Minimax search.

    This function recursively explores the game tree to estimate the
    utility of a board state, assuming optimal play from both players.
    It alternates between maximizing and minimizing layers depending
    on whose turn it is.

    The algorithm is implemented without alpha–beta pruning and relies
    on a heuristic evaluation function at leaf nodes.

    Parameters
    ----------
    board : Board
        The current board state.
    depth : int
        Remaining search depth. The search terminates when depth reaches
        zero.
    is_maximizing : bool
        Indicates whether the current node corresponds to the maximizing
        player (the AI) or the minimizing player (the opponent).
    ai_player : {'X', 'O'}
        The player symbol controlled by the AI. This defines the
        evaluation perspective throughout the search.

    Returns
    -------
    int
        The Minimax value (heuristic score) of the board state.
    """
    opponent = 'O' if ai_player == 'X' else 'X'

    # 1. Terminal states: win or loss
    if board.check_winner(ai_player):
        # Prefer faster wins
        return 10_000_000 + depth
    if board.check_winner(opponent):
        # Prefer slower losses
        return -10_000_000 - depth

    # 2. Base case: depth limit reached or draw
    if depth == 0 or board.is_full():
        return evaluate(board, board.player)

    moves = board.legal_moves()

    if is_maximizing:
        best_score = -float('inf')
        for move in moves:
            new_board = board.play(move)
            score = minimax(new_board, depth - 1, False, ai_player)
            best_score = max(best_score, score)
        return best_score
    else:
        best_score = float('inf')
        for move in moves:
            new_board = board.play(move)
            score = minimax(new_board, depth - 1, True, ai_player)
            best_score = min(best_score, score)
        return best_score


def find_best_move(board, depth=4):
    """
    Select the best move for the current player using Minimax search.

    This function serves as the entry point for the AI. It evaluates all
    legal moves from the current board state and returns the move with
    the highest Minimax value.

    Parameters
    ----------
    board : Board
        The current board state.
    depth : int, optional
        Maximum search depth for Minimax.

    Returns
    -------
    tuple[int, int] or None
        The selected move as a (row, column) pair, or None if no legal
        moves are available.
    """
    ai_player = board.player
    best_val = -float('inf')
    best_move = None

    moves = board.legal_moves()
    if not moves:
        return None

    # First layer of the Minimax tree: explicitly track moves
    for move in moves:
        new_board = board.play(move)
        move_val = minimax(new_board, depth - 1, False, ai_player)

        if move_val > best_val:
            best_val = move_val
            best_move = move

    return best_move

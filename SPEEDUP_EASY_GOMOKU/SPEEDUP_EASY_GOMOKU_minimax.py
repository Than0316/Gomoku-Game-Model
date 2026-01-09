from SPEEDUP_EASY_GOMOKU_shape import Shape
from SPEEDUP_EASY_GOMOKU_eval_function import evaluate


def minimax(board, depth, is_maximizing, ai_player):
    """
    Minimax adapted to MCTS-style Board.

    board: Board (MCTS-style)
    ai_player: 1 or 2 (player encoding as integers)
    legal_moves() returns a list of flat indices (ints)
    board.play(move) accepts int move and returns a new Board
    """
    opponent = 1 if ai_player == 2 else 2

    # 1. Terminal states: win or loss
    if board.check_winner(ai_player):
        # Prefer faster wins
        return 10_000_000 + depth
    if board.check_winner(opponent):
        # Prefer slower losses
        return -10_000_000 - depth

    # 2. Base case: depth limit reached or draw
    if depth == 0 or board.is_full():
        # Evaluate from perspective of board.current_player or given root?
        # to preserve original behaviour, evaluate from board.current_player
        return evaluate(board, board.current_player)

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
    Returns the best move as a flat index (int), or None if no moves.
    """
    ai_player = board.current_player
    best_val = -float('inf')
    best_move = None

    moves = board.legal_moves()
    if not moves:
        return None

    for move in moves:
        new_board = board.play(move)
        move_val = minimax(new_board, depth - 1, False, ai_player)

        if move_val > best_val:
            best_val = move_val
            best_move = move

    return best_move
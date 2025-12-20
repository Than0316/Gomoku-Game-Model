from EASY_GOMOKU_class_shape import Shape
from eval_fct import evaluate

def minimax(board, depth, is_maximizing, ai_player):
    """
    Simple Minimax algorithm without pruning.
    Returns the numeric score of a board state.
    """
    opponent = 'O' if ai_player == 'X' else 'X'
    
    # 1. Check for terminal states (Wins)
    if board.check_winner(ai_player):
        return 10_000_000 + depth  # Bonus for winning faster
    if board.check_winner(opponent):
        return -10_000_000 - depth # Penalty for losing faster
    
    # 2. Base case: Max depth or draw
    if depth == 0 or board.is_full():
        return evaluate(board, board.player)

    moves = board.legal_moves()
    
    if is_maximizing:
        best_score = -float('inf')
        for move in moves:
            # Simulate the move
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
    The entry point to find the best move using minimax.
    """
    ai_player = board.player
    best_val = -float('inf')
    best_move = None
    
    moves = board.legal_moves()
    if not moves:
        return None

    # We perform the first level of the loop here to track the actual move
    for move in moves:
        new_board = board.play(move)
        # Search child nodes (which will be minimizing player's turn)
        move_val = minimax(new_board, depth - 1, False, ai_player)
        
        if move_val > best_val:
            best_val = move_val
            best_move = move
            
    return best_move
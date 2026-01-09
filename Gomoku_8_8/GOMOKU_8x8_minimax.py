from GOMOKU_8x8_config import Config
from GOMOKU_8x8_eval import evaluate

def minimax(board, depth, alpha, beta, is_maximizing, ai_player):
    """
    Alpha-Beta Pruning Search.
    """
    opp = 'O' if ai_player == 'X' else 'X'
    
    # Terminal Check
    if board.check_winner(ai_player): return Config.SCORES['WIN'] + depth
    if board.check_winner(opp): return -Config.SCORES['WIN'] - depth
    
    # Leaf or Draw Check
    if depth == 0 or board.is_full():
        return evaluate(board, ai_player)

    moves = board.legal_moves()
    
    if is_maximizing:
        max_eval = -float('inf')
        for move in moves:
            eval_val = minimax(board.play(move), depth-1, alpha, beta, False, ai_player)
            max_eval = max(max_eval, eval_val)
            alpha = max(alpha, eval_val)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in moves:
            eval_val = minimax(board.play(move), depth-1, alpha, beta, True, ai_player)
            min_eval = min(min_eval, eval_val)
            beta = min(beta, eval_val)
            if beta <= alpha:
                break
        return min_eval

def find_best_move(board, depth=3):
    ai_player = board.player
    best_move = None
    best_val = -float('inf')
    alpha = -float('inf')
    beta = float('inf')
    
    moves = board.legal_moves()
    
    # Move Ordering Optimization:
    # We could sort 'moves' here based on a shallow eval to speed up pruning,
    # but for 8x8 depth 3, raw search is usually fast enough.
    
    for move in moves:
        new_board = board.play(move)
        
        # Instant win check (optimization)
        if new_board.check_winner(ai_player):
            return move
            
        move_val = minimax(new_board, depth-1, alpha, beta, False, ai_player)
        
        if move_val > best_val:
            best_val = move_val
            best_move = move
        
        # Update alpha for the root
        alpha = max(alpha, best_val)
        
    return best_move
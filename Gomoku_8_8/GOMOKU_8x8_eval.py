from Gomoku_8_8.GOMOKU_8x8_config import Config
from Gomoku_8_8.GOMOKU_8x8_shape import ShapeDetector

def evaluate(board, current_player):
    """
    Score the board.
    High negative score if opponent has unblocked threats.
    """
    ai_role = current_player
    opponent = 'O' if ai_role == 'X' else 'X'
    
    detector = ShapeDetector(board.grid)
    my_counts = detector.count_patterns(ai_role)
    opp_counts = detector.count_patterns(opponent)
    
    # 1. Instant End Game Checks
    if my_counts['WIN'] > 0: return Config.SCORES['WIN']
    if opp_counts['WIN'] > 0: return -Config.SCORES['WIN']
    
    # 2. Unstoppable Threats
    # If opponent has OPEN_4 (-XXXX-), we lose next turn guaranteed
    if opp_counts['OPEN_4'] > 0: return -Config.SCORES['WIN'] + 100
    # If we have OPEN_4, we win
    if my_counts['OPEN_4'] > 0: return Config.SCORES['WIN'] - 100

    # 3. Weighted Score
    score = 0
    score += my_counts['BLOCKED_4'] * Config.SCORES['BLOCKED_4']
    score += my_counts['OPEN_3'] * Config.SCORES['OPEN_3']
    score += my_counts['OPEN_2'] * Config.SCORES['OPEN_2']
    
    opp_score = 0
    opp_score += opp_counts['BLOCKED_4'] * Config.SCORES['BLOCKED_4']
    opp_score += opp_counts['OPEN_3'] * Config.SCORES['OPEN_3']
    opp_score += opp_counts['OPEN_2'] * Config.SCORES['OPEN_2']

    # 4. Defensive Panic Logic
    # If opponent has BLOCKED_4 (e.g. OXXXX-), we MUST block.
    # We apply a 5x multiplier to the penalty to override any offensive plans.
    if opp_counts['BLOCKED_4'] > 0:
        score -= opp_score * 10
    
    # If opponent has OPEN_3 (-XXX-), highly dangerous.
    elif opp_counts['OPEN_3'] > 0:
        score -= opp_score * 5
        
    else:
        # Standard balance
        score -= opp_score * 1.5

    return score
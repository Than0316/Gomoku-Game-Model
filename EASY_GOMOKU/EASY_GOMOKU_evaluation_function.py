# Scores for 4-in-a-row (6x6 board)
# We use very distinct score gaps to ensure the AI prioritizes correctly.
SCORES = {
    'WIN': 1_000_000_000,   # XXXX
    'OPEN_3': 1_000_000,    # -XXX- (Guaranteed win next turn)
    'BLOCKED_3': 50_000,    # XXX- or -XXX or XX-X (Requires immediate block)
    'OPEN_2': 5_000,        # -XX-
    'BLOCKED_2': 100,       # XX- or -XX
}

def get_all_lines(grid):
    """
    Extracts all horizontal, vertical, and diagonal lines from the board
    that are at least length 4 (since we can't make 4-in-a-row on shorter lines).
    """
    size = len(grid)
    lines = []

    # 1. Rows
    for r in range(size):
        lines.append("".join(grid[r]))

    # 2. Columns
    for c in range(size):
        col_str = "".join(grid[r][c] for r in range(size))
        lines.append(col_str)

    # 3. Diagonals
    # We only care about diagonals with length >= 4
    
    # Top-Left to Bottom-Right (k=0 is main diag, k>0 upper, k<0 lower)
    # The range for 6x6 to get len>=4 is roughly -2 to 2
    for k in range(-(size - 4), size - 4 + 1):
        diag = []
        for r in range(size):
            c = r + k
            if 0 <= c < size:
                diag.append(grid[r][c])
        lines.append("".join(diag))

    # Top-Right to Bottom-Left
    for k in range(3, 2 * size - 4): # Indices suitable for 6x6
        diag = []
        for r in range(size):
            c = k - r
            if 0 <= c < size:
                diag.append(grid[r][c])
        lines.append("".join(diag))

    return lines

def evaluate_line_string(line, player):
    """
    Scans a single string (e.g., "-XX-O-") for patterns and returns a score.
    """
    score = 0
    opponent = 'O' if player == 'X' else 'X'
    
    # We replace patterns we find with '#' to prevent double counting.
    # E.g. "XXXX" should be counted as WIN, not WIN + BLOCKED_3.
    
    # 1. Check for WIN (XXXX)
    if (player * 4) in line:
        return SCORES['WIN'] # Immediate return, game over logic handles this usually, but good for depth search
    
    # 2. Check for OPEN 3 (-XXX-)
    p_open3 = f"-{player*3}-"
    if p_open3 in line:
        score += SCORES['OPEN_3']
        line = line.replace(p_open3, "#####") # Consume

    # 3. Check for BLOCKED 3 / THREATS
    # Patterns: -XXX, XXX-, XX-X, X-XX
    threats = [
        f"-{player*3}", f"{player*3}-", 
        f"{player*2}-{player}", f"{player}-{player*2}"
    ]
    for pattern in threats:
        if pattern in line:
            score += SCORES['BLOCKED_3']
            line = line.replace(pattern, "####") # Consume to avoid overlapping lower scores

    # 4. Check for OPEN 2 (-XX-)
    p_open2 = f"-{player*2}-"
    if p_open2 in line:
        score += SCORES['OPEN_2']
        line = line.replace(p_open2, "####")

    # 5. Check for BLOCKED 2 (-XX, XX-)
    blocked_2 = [f"-{player*2}", f"{player*2}-"]
    for pattern in blocked_2:
        if pattern in line:
            score += SCORES['BLOCKED_2']
            line = line.replace(pattern, "###")
            
    return score

def evaluate(board, current_player):
    """
    Calculates the score of the board relative to the 'current_player'.
    """
    # Important: In Minimax, we need to know if the board is good for the AI ("Max")
    # or bad for the AI.
    
    # 'current_player' is who the AI is *currently* simulating.
    # But usually, we pass the 'root_player' (the AI's actual color) to simple minimax functions.
    # Assuming 'current_player' passed here is the AI maximizing player.
    
    opponent = 'O' if current_player == 'X' else 'X'
    
    lines = get_all_lines(board.grid)
    
    total_score = 0
    
    for line in lines:
        # Add my potential scores
        total_score += evaluate_line_string(line, current_player)
        
        # Subtract opponent's potential scores
        # We multiply by a factor (e.g. 1.2) to make the AI slightly defensive
        # This prevents it from ignoring a loss to chase a win of equal size.
        opp_score = evaluate_line_string(line, opponent)
        
        # Critical Defense Logic:
        # If opponent has an OPEN_3 (guaranteed win), that is essentially -Infinity for us.
        if opp_score >= SCORES['OPEN_3']:
            total_score -= SCORES['WIN'] * 0.9 # Massive penalty
        else:
            total_score -= opp_score

    return total_score
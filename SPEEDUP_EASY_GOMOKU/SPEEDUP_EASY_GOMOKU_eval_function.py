from SPEEDUP_EASY_GOMOKU_shape import Shape

SCORES = {
    'four_in_row': 1_000_000_000,   # XXXX
    'open_3': 1_000_000,            # -XXX-
    'jump_3': 10_000,               # XX-X or X-XX
    'blocked_3': 1_000,             # BXXX or OXXX
    'blocked_2': 100,               # BXX or OXX
    'open_2': 11_000,               # -XX-
    'single': 100,                  # X
}


def evaluate(board, root_player):
    """
    Heuristic evaluation adapted to MCTS-style Board.
    `root_player` should be 1 (X) or 2 (O).
    The Shape detector returns owner as 'X'/'O', so map accordingly.
    """
    shape_detector = Shape(board)
    shapes = shape_detector.detect_shapes()

    inv = {'X': 1, 'O': 2}
    opponent = 1 if root_player == 2 else 2
    total_score = 0

    for shape_type, owner_char in shapes:
        value = SCORES[shape_type]
        owner = inv[owner_char]

        if owner == root_player:
            total_score += value
        elif owner == opponent:
            # Opponent threats are penalized, with open threes treated
            # as near-winning configurations.
            if shape_type == 'open_3':
                total_score -= SCORES['four_in_row'] * 0.9
            else:
                total_score -= value

    return total_score
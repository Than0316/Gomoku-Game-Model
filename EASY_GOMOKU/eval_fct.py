from EASY_GOMOKU_class_shape import Shape

SCORES = {
    'four_in_row': 1_000_000_000,      # XXXX
    'open_3': 1_000_000,             # -XXX-
    'jump_3': 10_000,              # XX-X or X-XX
    'blocked_3': 1_000,            # BXXX or OXXX
    'blocked_2': 100,              # BXX or OXX
    'open_2': 11_000,              # -XX-
    'single': 100,                 # X
}

def evaluate(board, root_player):
    """
    Board evaluation from root_player's perspective.
    """

    shape_detector = Shape(board)
    shapes = shape_detector.detect_shapes()

    opponent = 'O' if root_player == 'X' else 'X'
    total_score = 0

    for shape_type, owner in shapes:
        value = SCORES[shape_type]

        if owner == root_player:
            total_score += value
        elif owner == opponent:
            if shape_type == 'open_3':
                total_score -= SCORES['four_in_row'] * 0.9
            else:
                total_score -= value

    return total_score
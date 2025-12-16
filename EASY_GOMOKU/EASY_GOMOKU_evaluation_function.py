from EASY_GOMOKU_class_shape import Shape

SCORES = {
    'four_in_row': 1_000_000,
    'open_3': 100_000,
    'jump_3': 10_000,
    'blocked_3': 1_000,
    'open_2': 100,
    'single': 1,
}

def evaluate(board, player):
    shape_detector = Shape(board)
    shapes = shape_detector.detect_shapes()
    score = 0
    for p_type, line, stone in shapes:
        if stone == player:
            score += SCORES[p_type]
        else:
            score -= SCORES[p_type]
    return score

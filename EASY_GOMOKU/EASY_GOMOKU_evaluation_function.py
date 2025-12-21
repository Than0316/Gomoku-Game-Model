from EASY_GOMOKU_class_shape import Shape

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
    Heuristic evaluation of a board state.

    This function assigns a scalar score to a Gomoku board state from
    the perspective of a designated root player. The evaluation is
    based on the detection of local stone patterns and a weighted
    scoring scheme reflecting their strategic importance.

    The score is positive if the position is favorable to the root
    player and negative if it favors the opponent.

    Parameters
    ----------
    board : Board
        The current board state to be evaluated.
    root_player : {'X', 'O'}
        The player for whom the evaluation is performed (typically the
        maximizing player in Minimax).

    Returns
    -------
    int
        A heuristic score representing the desirability of the board
        state for the root player.
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
            # Opponent threats are penalized, with open threes treated
            # as near-winning configurations.
            if shape_type == 'open_3':
                total_score -= SCORES['four_in_row'] * 0.9
            else:
                total_score -= value

    return total_score

SCORES = {
    'four_in_row': 1_000_000,      # XXXX
    'open_3': 100_000,             # -XXX-
    'jump_3': 10_000,              # XX-X or X-XX
    'blocked_3': 1_000,            # blocked by wall or opponent
    'open_2': 5_001,               # -XX-
    'single': 100,                 # X
}

def eval_function(shape):
    """
    Takes shapes in the list and returns the corresponding score.
    """
    total=0
    for (pattern_type, line, stone) in shape:
        score = SCORES.get(pattern_type, 0)
        if(stone == "X"):
            total+=score
        elif(stone=="O"):
            total-=score
    return total
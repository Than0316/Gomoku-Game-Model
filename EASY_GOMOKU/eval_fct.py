from EASY_GOMOKU_class_shape import Shape

def eval_function(shape):
    total=0
    for (pattern_type, line, stone) in shape:
        if(stone == "X"):
            total+=pattern_type
        elif(stone=="O"):
            total-=pattern_type
    return total
import re

# Patterns for string matching (optional, mostly for reference)
patterns = {
    'five': re.compile('11111'),
    'blockfive': re.compile('211111|111112'),
    'four': re.compile('011110'),
    'blockFour': re.compile(
        '10111|11011|11101|211110|211101|211011|210111|011112|101112|110112|111012'
    ),
    'three': re.compile('011100|011010|010110|001110'),
    'blockThree': re.compile('211100|211010|210110|001112|010112|011012'),
    'two': re.compile('001100|011000|000110|010100|001010'),
}

# Shape constants
class Shapes:
    FIVE = 5
    BLOCK_FIVE = 50
    FOUR = 4
    FOUR_FOUR = 44       # 双冲四
    FOUR_THREE = 43      # 冲四活三
    THREE_THREE = 33     # 双三
    BLOCK_FOUR = 40
    THREE = 3
    BLOCK_THREE = 30
    TWO_TWO = 22         # 双活二
    TWO = 2
    NONE = 0

# Performance counter (optional)
performance = {
    'five': 0, 'blockFive': 0, 'four': 0, 'blockFour': 0,
    'three': 0, 'blockThree': 0, 'two': 0, 'none': 0, 'total': 0
}


def count_shape(board, x, y, dx, dy, role):
    opponent = -role
    inner_empty = 0
    temp_empty = 0
    self_count = 0
    total_length = 0
    side_empty = 0
    no_empty_self = 0
    one_empty_self = 0

    size = len(board)

    for i in range(1, 6):
        nx, ny = x + i * dx, y + i * dy
        if not (0 <= nx < size and 0 <= ny < size):
            break
        current = board[nx][ny]
        if current == 2 or current == opponent:
            break
        if current == role:
            self_count += 1
            side_empty = 0
            if temp_empty:
                inner_empty += temp_empty
                temp_empty = 0
            if inner_empty == 0:
                no_empty_self += 1
                one_empty_self += 1
            elif inner_empty == 1:
                one_empty_self += 1
        total_length += 1
        if current == 0:
            temp_empty += 1
            side_empty += 1
        if side_empty >= 2:
            break
    if not inner_empty:
        one_empty_self = 0
    return {
        'self_count': self_count, 'total_length': total_length,
        'no_empty_self': no_empty_self, 'one_empty_self': one_empty_self,
        'inner_empty': inner_empty, 'side_empty': side_empty
    }


def get_shape_fast(board, x, y, dx, dy, role):
    size = len(board)
    if not (0 <= x+dx < size and 0 <= x-dx < size and 0 <= y+dy < size and 0 <= y-dy < size):
        return Shapes.NONE, 1

    left = count_shape(board, x, y, -dx, -dy, role)
    right = count_shape(board, x, y, dx, dy, role)

    self_count = left['self_count'] + right['self_count'] + 1
    total_length = left['total_length'] + right['total_length'] + 1
    no_empty_self = left['no_empty_self'] + right['no_empty_self'] + 1
    one_empty_self = max(left['one_empty_self'] + right['no_empty_self'],
                         left['no_empty_self'] + right['one_empty_self']) + 1
    left_empty = left['side_empty']
    right_empty = right['side_empty']

    shape = Shapes.NONE

    if total_length < 5:
        return shape, self_count

    if no_empty_self >= 5:
        shape = Shapes.FIVE if left_empty > 0 and right_empty > 0 else Shapes.BLOCK_FIVE
    elif no_empty_self == 4:
        if (left_empty >= 1 or left['one_empty_self'] > left['no_empty_self']) and \
           (right_empty >= 1 or right['one_empty_self'] > right['no_empty_self']):
            shape = Shapes.FOUR
        elif not (left_empty == 0 and right_empty == 0):
            shape = Shapes.BLOCK_FOUR
    elif one_empty_self == 4:
        shape = Shapes.BLOCK_FOUR
    elif no_empty_self == 3:
        if (left_empty >= 2 and right_empty >= 1) or (left_empty >= 1 and right_empty >= 2):
            shape = Shapes.THREE
        else:
            shape = Shapes.BLOCK_THREE
    elif one_empty_self == 3:
        shape = Shapes.THREE if left_empty >= 1 and right_empty >= 1 else Shapes.BLOCK_THREE
    elif (no_empty_self == 2 or one_empty_self == 2) and total_length > 5:
        shape = Shapes.TWO

    return shape, self_count


def is_five(shape):
    return shape in (Shapes.FIVE, Shapes.BLOCK_FIVE)


def is_four(shape):
    return shape in (Shapes.FOUR, Shapes.BLOCK_FOUR)


def get_all_shapes_of_point(shape_cache, x, y, role=None):
    roles = [role] if role else [1, -1]
    result = []
    for r in roles:
        for d in range(4):
            shape = shape_cache[r][d][x][y]
            if shape > 0:
                result.append(shape)
    return result

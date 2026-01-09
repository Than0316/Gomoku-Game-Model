# Shape detector adapted to the MCTS-style Board representation.
# It produces the same pattern strings as before, using 'X', 'O', '-' and 'B' for boundaries.
# Returns shapes as (pattern_type, owner_char) where owner_char is 'X' or 'O'.

class Shape:
    """
    Detect and classify local stone patterns on a Gomoku board.

    This version expects Board with:
      - SIZE attribute
      - states dict mapping idx -> player_int (1/2)
    """

    DIRECTIONS = [
        (1, 0),   # vertical
        (0, 1),   # horizontal
        (1, 1),   # main diagonal
        (1, -1),  # anti-diagonal
    ]

    def __init__(self, board):
        """
        board : Board (MCTS-style)
        """
        self.board_obj = board
        self.size = board.SIZE
        self.states = board.states
        self.player_char = {1: 'X', 2: 'O'}
        self.empty_char = '-'

    def _cell_char(self, r, c):
        if 0 <= r < self.size and 0 <= c < self.size:
            idx = r * self.size + c
            p = self.states.get(idx, 0)
            return self.player_char.get(p, self.empty_char)
        else:
            return 'B'  # boundary

    def get_line(self, row, column, direction_row, direction_column, length=4):
        """
        Extract a line segment and return a string of chars.
        """
        line = []
        for k in range(length):
            row_index = row + k * direction_row
            column_index = column + k * direction_column
            if 0 <= row_index < self.size and 0 <= column_index < self.size:
                line.append(self._cell_char(row_index, column_index))
            else:
                line.append('B')
        return ''.join(line)

    def detect_shapes(self):
        """
        Scan the board and detect patterns. Returns list of (pattern_type, owner_char).
        """
        shapes = []

        patterns = {
            'four_in_row': ['XXXX', 'OOOO'],
            'open_3': ['-XXX-', '-OOO-'],
            'jump_3': ['XX-X', 'X-XX', 'OO-O', 'O-OO'],
            'blocked_3': [
                'BXXX', 'XXXB', 'OXXX', 'XXXO',
                'BOOO', 'OOOB', 'XOOO', 'OOOX'
            ],
            'open_2': ['-XX-', '-OO-'],
            'blocked_2': [
                'BXX', 'XXB', 'BOO', 'OOB',
                'OXX', 'XXO', 'XOO', 'OOX'
            ],
            'single': ['X', 'O'],
        }

        for row in range(self.size):
            for column in range(self.size):
                stone_char = self._cell_char(row, column)
                if stone_char == self.empty_char or stone_char == 'B':
                    continue

                for direction_row, direction_column in self.DIRECTIONS:
                    line = ''
                    for k in range(-2, 3):
                        row_index = row + k * direction_row
                        column_index = column + k * direction_column
                        line += self._cell_char(row_index, column_index)

                    for pattern_type, pattern_strings in patterns.items():
                        for pattern in pattern_strings:
                            if pattern in line:
                                shapes.append((pattern_type, stone_char))

        return shapes
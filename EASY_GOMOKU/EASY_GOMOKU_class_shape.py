class Shape:
    """
    Detects all patterns (open 2, open 3, jump 3, blocked 3, etc.) on a Gomoku board.
    Blocked shapes are those blocked by the wall or the opponent.
    """

    DIRECTIONS = [(1,0), (0,1), (1,1), (1,-1)]  # vertical, horizontal, two diagonals

    def __init__(self, board):
        """
        board: an instance of Board
        """
        self.board = board.grid
        self.size = board.SIZE

    def get_line(self, row, column, direction_row, direction_column, length=4):
        """
        Returns a string of stones along a line starting at (row,column) 
        in direction (direction_row,direction_column),
        with 'B' for boundaries and opponent stones considered as block.
        """
        line = []
        for k in range(length):
            row_index = row + k*direction_row
            column_index = column + k*direction_column
            if 0 <= row_index < self.size and 0 <= column_index < self.size:
                line.append(self.board[row_index][column_index])
            else:
                line.append('B')  # boundary counts as block
        return ''.join(line)

    def detect_shapes(self):
        """
        Returns a list of all detected shapes in the board.
        Each shape is a tuple: (pattern_type, line_string, player)
        """
        shapes = []

        patterns = {
            'four_in_row': ['XXXX', 'OOOO'],
            'open_3': ['-XXX-', '-OOO-'],
            'jump_3': ['XX-X', 'X-XX', 'OO-O', 'O-OO'],
            'blocked_3': ['BXXX', 'XXXB', 'OXXX', 'XXXO', 'BOOO', 'OOOB', 'XOOO', 'OOOX'],
            'open_2': ['-XX-', '-OO-'],
            'blocked_2':['BXX', 'XXB', 'BOO', 'OOB', 'OXX', 'XXO', 'XOO', 'OOX'],
            'single': ['X', 'O'],
        }

        for row in range(self.size):
            for column in range(self.size):
                stone = self.board[row][column]
                if stone == '-':
                    continue
                for direction_row, direction_column in self.DIRECTIONS:
                    line = ''
                    for k in range(-2, 3):  # look 2 before and 2 after
                        row_index = row + k*direction_row
                        column_index = column + k*direction_column
                        if 0 <= row_index < self.size and 0 <= column_index < self.size:
                            line += self.board[row_index][column_index]
                        else:
                            line += 'B'  # boundary counts as block

                    for pattern_type, pattern_string in patterns.items():
                        for pattern in pattern_string:
                            if pattern in line:
                                shapes.append((pattern_type, stone))
        return shapes

class Shape:
    """
    Detect and classify local stone patterns on a Gomoku board.

    This class is responsible for identifying strategically relevant
    configurations (e.g., open three, jump three, blocked patterns)
    for both players. Detected patterns are later used by the heuristic
    evaluation function to score board states.

    Boundaries of the board and opponent stones are treated as blocking
    elements when identifying patterns.
    """

    DIRECTIONS = [
        (1, 0),   # vertical
        (0, 1),   # horizontal
        (1, 1),   # main diagonal
        (1, -1),  # anti-diagonal
    ]

    def __init__(self, board):
        """
        Initialize the shape detector.

        Parameters
        ----------
        board : Board
            An instance of the Board class representing the current
            game state.
        """
        self.board = board.grid
        self.size = board.SIZE

    def get_line(self, row, column, direction_row, direction_column, length=4):
        """
        Extract a line segment from the board in a given direction.

        The method returns a string representation of stones starting
        from a given position and extending in a specified direction.
        Board boundaries are encoded using the symbol 'B', which is
        treated as a blocking element.

        Parameters
        ----------
        row : int
            Starting row index.
        column : int
            Starting column index.
        direction_row : int
            Row increment defining the direction.
        direction_column : int
            Column increment defining the direction.
        length : int, optional
            Number of consecutive positions to extract.

        Returns
        -------
        str
            A string encoding the extracted line segment, consisting of
            player stones, empty cells, or boundary markers ('B').
        """
        line = []
        for k in range(length):
            row_index = row + k * direction_row
            column_index = column + k * direction_column
            if 0 <= row_index < self.size and 0 <= column_index < self.size:
                line.append(self.board[row_index][column_index])
            else:
                line.append('B')  # boundary counts as block
        return ''.join(line)

    def detect_shapes(self):
        """
        Detect all predefined patterns present on the board.

        The method scans the board in all principal directions and
        identifies occurrences of predefined local patterns such as
        open threes, jump threes, blocked patterns, and four-in-a-row.
        Each detected pattern is associated with the player stone
        that generated it.

        Returns
        -------
        list[tuple[str, str]]
            A list of detected shapes. Each element is a tuple
            ``(pattern_type, stone)``, where ``pattern_type`` is the
            name of the detected configuration and ``stone`` is the
            corresponding player symbol ('X' or 'O').
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
                stone = self.board[row][column]
                if stone == '-':
                    continue

                for direction_row, direction_column in self.DIRECTIONS:
                    line = ''
                    for k in range(-2, 3):
                        row_index = row + k * direction_row
                        column_index = column + k * direction_column
                        if 0 <= row_index < self.size and 0 <= column_index < self.size:
                            line += self.board[row_index][column_index]
                        else:
                            line += 'B'  # boundary counts as block

                    for pattern_type, pattern_strings in patterns.items():
                        for pattern in pattern_strings:
                            if pattern in line:
                                shapes.append((pattern_type, stone))

        return shapes
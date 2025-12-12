from GOMOKU_config import Config
from GOMOKU_class_shape import ShapeDetector, ShapeType

# --- Score Constants ---
FIVE = 10000000
BLOCK_FIVE = FIVE
FOUR = 100000
FOUR_FOUR = FOUR            # Double Four
FOUR_THREE = FOUR           # Four-Three
THREE_THREE = FOUR // 2     # Double Three
BLOCK_FOUR = 1500
THREE = 1000
BLOCK_THREE = 150
TWO_TWO = 200               # Double Two
TWO = 100
BLOCK_TWO = 15
ONE = 10
BLOCK_ONE = 1

def get_real_shape_score(shape_type):
    """Maps a ShapeType to a numerical score."""
    if shape_type == ShapeType.FIVE: return FIVE
    if shape_type == ShapeType.BLOCK_FIVE: return BLOCK_FOUR
    if shape_type == ShapeType.FOUR: return THREE
    if shape_type == ShapeType.FOUR_FOUR: return THREE
    if shape_type == ShapeType.FOUR_THREE: return THREE
    if shape_type == ShapeType.BLOCK_FOUR: return BLOCK_THREE
    if shape_type == ShapeType.THREE: return TWO
    if shape_type == ShapeType.THREE_THREE: return THREE_THREE // 10
    if shape_type == ShapeType.BLOCK_THREE: return BLOCK_TWO
    if shape_type == ShapeType.TWO: return ONE
    if shape_type == ShapeType.TWO_TWO: return TWO_TWO // 10
    return 0

class Evaluator:
    def __init__(self, size=Config.size):
        self.size = size
        # Board with padding (2 = wall)
        self.board = [[2 for _ in range(size + 2)] for _ in range(size + 2)]
        for i in range(size):
            for j in range(size):
                self.board[i + 1][j + 1] = 0

        # Positional Scores: [x][y] = Score
        self.black_scores = [[0 for _ in range(size)] for _ in range(size)]
        self.white_scores = [[0 for _ in range(size)] for _ in range(size)]

        # Shape Cache: [role][direction][x][y] = ShapeType
        # Roles mapped: 1 -> index 0, -1 -> index 1
        self.shape_cache = {
            1: [ [[ShapeType.NONE] * self.size for _ in range(self.size)] for _ in range(4) ],
            -1: [ [[ShapeType.NONE] * self.size for _ in range(self.size)] for _ in range(4) ]
        }
        
        # Directions: Horizontal, Vertical, Diagonal \, Diagonal /
        self.directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        # Initialize points
        # In a real game, you might call this, or rely on incremental updates from empty
        # self.init_points() 

    def move(self, x, y, role):
        """Updates the board and scores for a move."""
        # 1. Clear cache for this specific point (it's no longer a potential shape spot)
        for d in range(4):
            self.shape_cache[role][d][x][y] = ShapeType.NONE
            self.shape_cache[-role][d][x][y] = ShapeType.NONE
        
        self.black_scores[x][y] = 0
        self.white_scores[x][y] = 0

        # 2. Place stone (Adjust for padding)
        self.board[x + 1][y + 1] = role
        
        # 3. Update neighbors
        self.update_point(x, y)

    def undo(self, x, y):
        """Undoes a move and recalculates scores."""
        self.board[x + 1][y + 1] = 0
        self.update_point(x, y)

    def update_point(self, x, y):
        """Updates scores for the point and its surrounding neighbors."""
        # Check self (now empty or occupied)
        self._update_single_point(x, y, 1)
        self._update_single_point(x, y, -1)

        # Check neighbors 5 steps out
        for d_idx, (ox, oy) in enumerate(self.directions):
            for sign in [1, -1]:
                for step in range(1, 6):
                    nx, ny = x + sign * step * ox, y + sign * step * oy
                    
                    if not (0 <= nx < self.size and 0 <= ny < self.size): break
                    val = self.board[nx + 1][ny + 1]
                    if val == 2: break # Wall
                    if val != 0: continue # Occupied
                    
                    self._update_single_point(nx, ny, 1, d_idx)
                    self._update_single_point(nx, ny, -1, d_idx)

    def _update_single_point(self, x, y, role, only_direction=None):
        """Calculates heuristic score for a single point."""
        if self.board[x + 1][y + 1] != 0: return 0

        # Temp place
        self.board[x + 1][y + 1] = role
        
        dirs = [only_direction] if only_direction is not None else range(4)
        
        for d in dirs:
            ox, oy = self.directions[d]
            shape, _ = ShapeDetector.get_shape(self._get_pure_board(), x, y, ox, oy, role)
            self.shape_cache[role][d][x][y] = shape

        # Aggregate totals
        total_score = 0
        block_four = 0
        three = 0
        two = 0

        for d in range(4):
            shape = self.shape_cache[role][d][x][y]
            if shape != ShapeType.NONE:
                total_score += get_real_shape_score(shape)
                if shape == ShapeType.BLOCK_FOUR: block_four += 1
                if shape == ShapeType.THREE: three += 1
                if shape == ShapeType.TWO: two += 1
        
        # Compound shape bonuses
        if block_four >= 2: total_score += get_real_shape_score(ShapeType.FOUR_FOUR)
        elif block_four and three: total_score += get_real_shape_score(ShapeType.FOUR_THREE)
        elif three >= 2: total_score += get_real_shape_score(ShapeType.THREE_THREE)
        elif two >= 2: total_score += get_real_shape_score(ShapeType.TWO_TWO)

        # Remove temp
        self.board[x + 1][y + 1] = 0

        if role == 1: self.black_scores[x][y] = total_score
        else: self.white_scores[x][y] = total_score
        
        return total_score

    def evaluate(self, role):
        """Returns the total score difference."""
        black_total = sum(sum(row) for row in self.black_scores)
        white_total = sum(sum(row) for row in self.white_scores)
        return (black_total - white_total) if role == 1 else (white_total - black_total)

    def _get_pure_board(self):
        """Strip padding for ShapeDetector."""
        return [[self.board[i+1][j+1] for j in range(self.size)] for i in range(self.size)]
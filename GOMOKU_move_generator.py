from GOMOKU_config import Config
from GOMOKU_class_shape import ShapeType
from GOMOKU_class_board import Board ###___### get_valuable_moves (two positions next to existing stones)

class MoveGenerator:
    def __init__(self, evaluator):
        self.evaluator = evaluator
        self.size = evaluator.size

    def get_moves(self, role, depth=0, only_three=False, only_four=False):
        """
        Generates a list of candidate moves (x, y).
        Prioritizes winning moves, blocking moves, and high-score moves.
        """
        # 1. Categorize points by the shapes they create
        points = {
            ShapeType.FIVE: set(),
            ShapeType.BLOCK_FIVE: set(),
            ShapeType.FOUR: set(),
            ShapeType.BLOCK_FOUR: set(),
            ShapeType.FOUR_FOUR: set(),
            ShapeType.FOUR_THREE: set(),
            ShapeType.THREE_THREE: set(),
            ShapeType.THREE: set(),
            ShapeType.BLOCK_THREE: set(),
            ShapeType.TWO: set()
        }

        # Check shapes for BOTH players (Self and Opponent)
        # We want to find our winning moves OR block their winning moves
        for r in [role, -role]:
            for i in range(self.size): ###___### for candidate_moves in get_valuable_moves
                for j in range(self.size):
                    if self.evaluator.board[i+1][j+1] != 0: continue
                    
                    fours = 0
                    block_fours = 0
                    threes = 0
                    
                    for d in range(4):
                        shape = self.evaluator.shape_cache[r][d][i][j]
                        if shape == ShapeType.NONE: continue
                        
                        if shape == ShapeType.FIVE: points[ShapeType.FIVE].add((i, j))
                        elif shape == ShapeType.BLOCK_FIVE: points[ShapeType.BLOCK_FIVE].add((i, j))
                        elif shape == ShapeType.FOUR: 
                            points[ShapeType.FOUR].add((i, j))
                            fours += 1
                        elif shape == ShapeType.BLOCK_FOUR: 
                            points[ShapeType.BLOCK_FOUR].add((i, j))
                            block_fours += 1
                        elif shape == ShapeType.THREE: 
                            points[ShapeType.THREE].add((i, j))
                            threes += 1
                        elif shape == ShapeType.BLOCK_THREE: points[ShapeType.BLOCK_THREE].add((i, j))
                        elif shape == ShapeType.TWO: points[ShapeType.TWO].add((i, j))
                    
                    # Compound Logic
                    if fours >= 2: points[ShapeType.FOUR_FOUR].add((i, j))
                    elif block_fours and threes: points[ShapeType.FOUR_THREE].add((i, j))
                    elif threes >= 2: points[ShapeType.THREE_THREE].add((i, j))

        # --- Priority 1: Instant Win (Five) ---
        fives = points[ShapeType.FIVE].union(points[ShapeType.BLOCK_FIVE])
        if fives: 
            return list(fives)

        # --- Priority 2: Force Win/Block (Four) ---
        # If there is a 4, we MUST play it (to win or to block)
        fours = points[ShapeType.FOUR].union(points[ShapeType.BLOCK_FOUR])
        if only_four:
            return list(fours)
        if fours:
            return list(fours)

        # --- Priority 3: High Threat (Double 3, 4-3) ---
        compounds = points[ShapeType.FOUR_FOUR].union(points[ShapeType.FOUR_THREE]).union(points[ShapeType.THREE_THREE])
        if compounds:
            return list(compounds.union(points[ShapeType.THREE]))

        if only_three:
            return list(points[ShapeType.THREE])

        # --- Priority 4: General High Value Moves ---
        candidates = set()
        candidates.update(points[ShapeType.BLOCK_THREE])
        candidates.update(points[ShapeType.TWO])
        candidates.update(points[ShapeType.THREE])
        
        # If we don't have specific shapes, pick the highest scores from the evaluator tables
        if len(candidates) < Config.points_limit:
             all_spots = []
             for i in range(self.size):
                 for j in range(self.size):
                     if self.evaluator.board[i+1][j+1] == 0:
                         # Score = My Attack Potential + My Defense Necessity (Opponent's score)
                         score = self.evaluator.black_scores[i][j] + self.evaluator.white_scores[i][j]
                         if score > 0:
                             all_spots.append(((i, j), score))
             
             all_spots.sort(key=lambda x: x[1], reverse=True)
             return [x[0] for x in all_spots[:Config.points_limit]]

        return list(candidates)[:Config.points_limit]
import copy
from collections import defaultdict

# Assuming `shapes`, `getShapeFast`, etc. are defined elsewhere or need to be ported.
# For now, let's use placeholders for those.

class Config:
    onlyInLine = False
    inlineCount = 2
    inLineDistance = 4
    pointsLimit = 20

config = Config()

class Shapes:
    NONE = 0
    FIVE = 1
    BLOCK_FIVE = 2
    FOUR = 3
    FOUR_FOUR = 4
    FOUR_THREE = 5
    THREE_THREE = 6
    BLOCK_FOUR = 7
    THREE = 8
    BLOCK_THREE = 9
    TWO_TWO = 10
    TWO = 11

shapes = Shapes()

# Placeholder scoring - adapt to your game's scoring model.
SCORES = {
    Shapes.FIVE: 10000000,
    Shapes.BLOCK_FIVE: 10000000,
    Shapes.FOUR: 100000,
    Shapes.FOUR_FOUR: 100000,
    Shapes.FOUR_THREE: 100000,
    Shapes.THREE_THREE: 50000,
    Shapes.BLOCK_FOUR: 1500,
    Shapes.THREE: 1000,
    Shapes.BLOCK_THREE: 150,
    Shapes.TWO_TWO: 200,
    Shapes.TWO: 100,
    Shapes.BLOCK_TWO: 15,
    Shapes.ONE: 10 if hasattr(shapes, 'ONE') else 10,
    Shapes.BLOCK_ONE: 1 if hasattr(shapes, 'BLOCK_ONE') else 1,
    Shapes.NONE: 0,
}

# Directions: Horizontal, Vertical, Diagonal, Anti-diagonal
ALL_DIRECTIONS = [
    (0, 1),
    (1, 0),
    (1, 1),
    (1, -1)
]

def direction2index(ox, oy):
    if ox == 0:
        return 0
    if oy == 0:
        return 1
    if ox == oy:
        return 2
    return 3

def getRealShapeScore(shape):
    # Replicating the JS logic
    if shape == Shapes.FIVE:
        return SCORES[Shapes.FOUR]
    elif shape == Shapes.BLOCK_FIVE:
        return SCORES[Shapes.BLOCK_FOUR]
    elif shape == Shapes.FOUR or shape == Shapes.FOUR_FOUR or shape == Shapes.FOUR_THREE:
        return SCORES[Shapes.THREE]
    elif shape == Shapes.BLOCK_FOUR:
        return SCORES[Shapes.BLOCK_THREE]
    elif shape == Shapes.THREE:
        return SCORES[Shapes.TWO]
    elif shape == Shapes.THREE_THREE:
        return SCORES[Shapes.THREE_THREE] // 10
    elif shape == Shapes.BLOCK_THREE:
        return SCORES[Shapes.BLOCK_TWO]
    elif shape == Shapes.TWO:
        return SCORES[Shapes.ONE]
    elif shape == Shapes.TWO_TWO:
        return SCORES[Shapes.TWO_TWO] // 10
    else:
        return 0

def coordinate2Position(x, y, size):
    return x * size + y

def position2Coordinate(pos, size):
    x = pos // size
    y = pos % size
    return (x, y)

def isFour(shape):
    return shape in [Shapes.FOUR, Shapes.BLOCK_FOUR, Shapes.FOUR_FOUR, Shapes.FOUR_THREE]

def isFive(shape):
    return shape in [Shapes.FIVE, Shapes.BLOCK_FIVE]

def getAllShapesOfPoint(shapeCache, x, y, role):
    result = []
    for direction in range(4):
        s = shapeCache[role][direction][x][y]
        if s != Shapes.NONE:
            result.append(s)
    return result

def hasInLine(point, lastPoints, size):
    # Placeholder logic
    return point in lastPoints

class Evaluate:
    def __init__(self, size=15):
        self.size = size
        self.board = [[2 if i == 0 or j == 0 or i == size + 1 or j == size + 1 else 0 for j in range(size + 2)] for i in range(size + 2)]
        self.blackScores = [[0 for _ in range(size)] for _ in range(size)]
        self.whiteScores = [[0 for _ in range(size)] for _ in range(size)]
        self.initPoints()
        self.history = []

    def move(self, x, y, role):
        for d in range(4):
            self.shapeCache[role][d][x][y] = shapes.NONE
            self.shapeCache[-role][d][x][y] = shapes.NONE
        self.blackScores[x][y] = 0
        self.whiteScores[x][y] = 0
        self.board[x+1][y+1] = role
        self.updatePoint(x, y)
        self.history.append([coordinate2Position(x, y, self.size), role])

    def undo(self, x, y):
        self.board[x+1][y+1] = 0
        self.updatePoint(x, y)
        self.history.pop()

    def initPoints(self):
        self.shapeCache = {}
        for role in [1, -1]:
            self.shapeCache[role] = {}
            for direction in range(4):
                self.shapeCache[role][direction] = [[shapes.NONE for _ in range(self.size)] for _ in range(self.size)]
        self.pointsCache = {}
        for role in [1, -1]:
            self.pointsCache[role] = {}
            for shape in vars(shapes).values():
                self.pointsCache[role][shape] = set()

    def getPointsInLine(self, role):
        pointsInLine = defaultdict(set)
        hasPointsInLine = False
        last2Points = [p for p, r in self.history[-config.inlineCount:]]
        processed = dict()
        for r in [role, -role]:
            for point in last2Points:
                x, y = position2Coordinate(point, self.size)
                for ox, oy in ALL_DIRECTIONS:
                    for sign in [1, -1]:
                        for step in range(1, config.inLineDistance+1):
                            nx, ny = x + sign * step * ox, y + sign * step * oy
                            position = coordinate2Position(nx, ny, self.size)
                            if nx < 0 or nx >= self.size or ny < 0 or ny >= self.size:
                                break
                            if self.board[nx+1][ny+1] != 0:
                                continue
                            if processed.get(position) == r:
                                continue
                            processed[position] = r
                            for direction in range(4):
                                shape = self.shapeCache[r][direction][nx][ny]
                                if shape:
                                    pointsInLine[shape].add(coordinate2Position(nx, ny, self.size))
                                    hasPointsInLine = True
        if hasPointsInLine:
            return pointsInLine
        return False

    def getPoints(self, role, depth, vct, vcf):
        first = role if depth % 2 == 0 else -role
        if config.onlyInLine and len(self.history) >= config.inlineCount:
            pointsInLine = self.getPointsInLine(role)
            if pointsInLine:
                return pointsInLine

        points = defaultdict(set)
        lastPoints = [p for p, r in self.history[-4:]]

        for r in [role, -role]:
            for i in range(self.size):
                for j in range(self.size):
                    fourCount, blockFourCount, threeCount = 0, 0, 0
                    for direction in range(4):
                        if self.board[i+1][j+1] != 0:
                            continue
                        shape = self.shapeCache[r][direction][i][j]
                        if not shape:
                            continue
                        point = i * self.size + j
                        if vct:
                            if depth % 2 == 0:
                                if depth == 0 and r != first: continue
                                if shape != shapes.THREE and not isFour(shape) and not isFive(shape): continue
                                if shape == shapes.THREE and r != first: continue
                                if depth == 0 and r != first: continue
                                if depth > 0:
                                    if shape == shapes.THREE and len(getAllShapesOfPoint(self.shapeCache, i, j, r)) == 1: continue
                                    if shape == shapes.BLOCK_FOUR and len(getAllShapesOfPoint(self.shapeCache, i, j, r)) == 1: continue
                            else:
                                if shape != shapes.THREE and not isFour(shape) and not isFive(shape): continue
                                if shape == shapes.THREE and r == -first: continue
                                if depth > 1:
                                    if shape == shapes.BLOCK_FOUR and len(getAllShapesOfPoint(self.shapeCache, i, j, r)) == 1: continue
                                    if shape == shapes.BLOCK_FOUR and not hasInLine(point, lastPoints, self.size): continue
                        if vcf:
                            if not isFour(shape) and not isFive(shape):
                                continue
                        if depth > 2 and shape in [shapes.TWO, shapes.TWO_TWO, shapes.BLOCK_THREE] and not hasInLine(point, lastPoints, self.size):
                            continue
                        points[shape].add(point)
                        if shape == shapes.FOUR:
                            fourCount += 1
                        elif shape == shapes.BLOCK_FOUR:
                            blockFourCount += 1
                        elif shape == shapes.THREE:
                            threeCount += 1
                        unionShape = None
                        if fourCount >= 2:
                            unionShape = shapes.FOUR_FOUR
                        elif blockFourCount and threeCount:
                            unionShape = shapes.FOUR_THREE
                        elif threeCount >= 2:
                            unionShape = shapes.THREE_THREE
                        if unionShape:
                            points[unionShape].add(point)
        return points

    def updatePoint(self, x, y):
        self.updateSinglePoint(x, y, 1)
        self.updateSinglePoint(x, y, -1)
        for ox, oy in ALL_DIRECTIONS:
            for sign in [1, -1]:
                for step in range(1, 6):
                    reachEdge = False
                    for role in [1, -1]:
                        nx, ny = x + sign * step * ox + 1, y + sign * step * oy + 1
                        if self.board[nx][ny] == 2:
                            reachEdge = True
                            break
                        elif self.board[nx][ny] == -role:
                            continue
                        elif self.board[nx][ny] == 0:
                            self.updateSinglePoint(nx-1, ny-1, role, (sign*ox, sign*oy))
                    if reachEdge:
                        break

    def updateSinglePoint(self, x, y, role, direction=None):
        if self.board[x+1][y+1] != 0:
            return  # not empty
        self.board[x+1][y+1] = role
        directions = [direction] if direction else ALL_DIRECTIONS
        shapeCache = self.shapeCache[role]
        for ox, oy in directions:
            shapeCache[direction2index(ox, oy)][x][y] = shapes.NONE

        score = 0
        blockfourCount, threeCount, twoCount = 0, 0, 0
        for intDirection in range(4):
            shape = shapeCache[intDirection][x][y]
            if shape > shapes.NONE:
                score += getRealShapeScore(shape)
                if shape == shapes.BLOCK_FOUR: blockfourCount += 1
                if shape == shapes.THREE: threeCount += 1
                if shape == shapes.TWO: twoCount += 1
        for ox, oy in directions:
            intDirection = direction2index(ox, oy)
            shape, selfCount = None, None  # Replace with actual getShapeFast logic as needed
            # --- getShapeFast should be implemented according to your game rules ---
            # For now, we use shapes.NONE to avoid errors.
            shape = shapes.NONE
            # --- end placeholder ---
            if not shape: continue
            shapeCache[intDirection][x][y] = shape
            if shape == shapes.BLOCK_FOUR: blockfourCount += 1
            if shape == shapes.THREE: threeCount += 1
            if shape == shapes.TWO: twoCount += 1
            if blockfourCount >= 2:
                shape = shapes.FOUR_FOUR
            elif blockfourCount and threeCount:
                shape = shapes.FOUR_THREE
            elif threeCount >= 2:
                shape = shapes.THREE_THREE
            elif twoCount >= 2:
                shape = shapes.TWO_TWO
            score += getRealShapeScore(shape)
        self.board[x+1][y+1] = 0
        if role == 1:
            self.blackScores[x][y] = score
        else:
            self.whiteScores[x][y] = score
        return score

    def evaluate(self, role):
        blackScore = sum(sum(row) for row in self.blackScores)
        whiteScore = sum(sum(row) for row in self.whiteScores)
        return blackScore - whiteScore if role == 1 else whiteScore - blackScore

    def getMoves(self, role, depth, onThree=False, onlyFour=False):
        moves = [divmod(move, self.size) for move in self._getMoves(role, depth, onThree, onlyFour)]
        return moves

    def _getMoves(self, role, depth, onlyThree=False, onlyFour=False):
        points = self.getPoints(role, depth, onlyThree, onlyFour)
        fives = points[shapes.FIVE]
        blockFives = points[shapes.BLOCK_FIVE]
        if fives or blockFives:
            return set(fives | blockFives)
        fours = points[shapes.FOUR]
        blockfours = points[shapes.BLOCK_FOUR]
        if onlyFour or fours:
            return set(fours | blockfours)
        four_fours = points[shapes.FOUR_FOUR]
        if four_fours:
            return set(four_fours | blockfours)
        threes = points[shapes.THREE]
        four_threes = points[shapes.FOUR_THREE]
        if four_threes:
            return set(four_threes | blockfours | threes)
        three_threes = points[shapes.THREE_THREE]
        if three_threes:
            return set(three_threes | blockfours | threes)
        if onlyThree:
            return set(blockfours | threes)
        blockthrees = points[shapes.BLOCK_THREE]
        two_twos = points[shapes.TWO_TWO]
        twos = points[shapes.TWO]
        res = set(list(blockfours | threes | blockthrees | two_twos | twos)[:config.pointsLimit])
        return res

    def display(self):
        result = ''
        for i in range(1, self.size + 1):
            for j in range(1, self.size + 1):
                val = self.board[i][j]
                if val == 1:
                    result += 'O '
                elif val == -1:
                    result += 'X '
                else:
                    result += '- '
            result += '\n'
        print(result)
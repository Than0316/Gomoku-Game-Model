from zobrist import Zobrist
from cache import Cache
from eval import Evaluate, FIVE

class Board:
    def __init__(self, size=15, first_role=1):
        self.size = size
        self.board = [[0 for _ in range(size)] for _ in range(size)]
        self.first_role = first_role  # 1 for black, -1 for white
        self.role = first_role
        self.history = []

        self.zobrist = Zobrist(self.size)
        self.winner_cache = Cache()
        self.gameover_cache = Cache()
        self.evaluate_cache = Cache()
        self.valuable_moves_cache = Cache()
        self.evaluate_time = 0

        self.evaluator = Evaluate(self.size)

    def is_game_over(self):
        hash_ = self.hash()
        cached = self.gameover_cache.get(hash_)
        if cached is not None:
            return cached

        if self.get_winner() != 0:
            self.gameover_cache.put(hash_, True)
            return True

        # Check for empty spaces
        for row in self.board:
            if 0 in row:
                self.gameover_cache.put(hash_, False)
                return False

        self.gameover_cache.put(hash_, True)
        return True

    def get_winner(self):
        hash_ = self.hash()
        cached = self.winner_cache.get(hash_)
        if cached is not None:
            return cached

        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # Horizontal, vertical, diagonals
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0:
                    continue
                role = self.board[i][j]
                for dx, dy in directions:
                    count = 0
                    x, y = i, j
                    while 0 <= x < self.size and 0 <= y < self.size and self.board[x][y] == role:
                        count += 1
                        x += dx
                        y += dy
                    if count >= 5:
                        self.winner_cache.put(hash_, role)
                        return role

        self.winner_cache.put(hash_, 0)
        return 0

    def get_valid_moves(self):
        return [[i, j] for i in range(self.size) for j in range(self.size) if self.board[i][j] == 0]

    def put(self, i, j, role=None):
        if role is None:
            role = self.role

        if not (0 <= i < self.size and 0 <= j < self.size):
            print("Invalid move: out of bounds!", i, j)
            return False

        if self.board[i][j] != 0:
            print("Invalid move: position occupied!", i, j)
            return False

        self.board[i][j] = role
        self.history.append({'i': i, 'j': j, 'role': role})
        self.zobrist.toggle_piece(i, j, role)
        self.evaluator.move(i, j, role)
        self.role *= -1
        return True

    def undo(self):
        if not self.history:
            print("No moves to undo!")
            return False

        last_move = self.history.pop()
        i, j, role = last_move['i'], last_move['j'], last_move['role']
        self.board[i][j] = 0
        self.role = role
        self.zobrist.toggle_piece(i, j, role)
        self.evaluator.undo(i, j)
        return True

    def position2coordinate(self, position):
        return [position // self.size, position % self.size]

    def coordinate2position(self, coordinate):
        return coordinate[0] * self.size + coordinate[1]

    def get_valuable_moves(self, role, depth=0, only_three=False, only_four=False):
        hash_ = self.hash()
        prev = self.valuable_moves_cache.get(hash_)
        if prev and prev['role'] == role and prev['depth'] == depth and prev['only_three'] == only_three and prev['only_four'] == only_four:
            return prev['moves']

        moves = self.evaluator.get_moves(role, depth, only_three, only_four)
        if not only_three and not only_four:
            center = self.size // 2
            if self.board[center][center] == 0:
                moves.append([center, center])

        self.valuable_moves_cache.put(hash_, {
            'role': role,
            'moves': moves,
            'depth': depth,
            'only_three': only_three,
            'only_four': only_four
        })
        return moves

    def display(self, extra_points=None):
        if extra_points is None:
            extra_points = []

        extra_positions = [self.coordinate2position(p) for p in extra_points]
        result = ''
        for i in range(self.size):
            for j in range(self.size):
                pos = self.coordinate2position([i, j])
                if pos in extra_positions:
                    result += '? '
                elif self.board[i][j] == 1:
                    result += 'O '
                elif self.board[i][j] == -1:
                    result += 'X '
                else:
                    result += '- '
            result += '\n'
        return result

    def hash(self):
        return self.zobrist.get_hash()

    def evaluate(self, role):
        hash_ = self.hash()
        prev = self.evaluate_cache.get(hash_)
        if prev and prev['role'] == role:
            return prev['score']

        winner = self.get_winner()
        if winner != 0:
            score = FIVE * winner * role
        else:
            score = self.evaluator.evaluate(role)

        self.evaluate_cache.put(hash_, {'role': role, 'score': score})
        return score

    def reverse(self):
        new_board = Board(self.size, -self.first_role)
        for move in self.history:
            new_board.put(move['i'], move['j'], -move['role'])
        return new_board

    def __str__(self):
        return '\n'.join(''.join(str(cell) for cell in row) for row in self.board)

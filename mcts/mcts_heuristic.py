import numpy as np
from operator import itemgetter
from .mcts_pure import MCTS, MCTSPlayer

def check_win_local(states, move, player, size=8, n_win=5):
    """
    Checks if placing a stone at 'move' creates a win.
    OPTIMIZATION: Only checks the 4 lines passing through 'move'.
    This is mathematically identical to scanning the whole board but O(1).
    """
    r, c = divmod(move, size)
    # Directions: Horizontal, Vertical, Diag \, Diag /
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    
    for dr, dc in directions:
        count = 1
        # Scan forward
        for k in range(1, n_win):
            nr, nc = r + k*dr, c + k*dc
            if not (0 <= nr < size and 0 <= nc < size): break
            if states.get(nr * size + nc) != player: break
            count += 1
        # Scan backward
        for k in range(1, n_win):
            nr, nc = r - k*dr, c - k*dc
            if not (0 <= nr < size and 0 <= nc < size): break
            if states.get(nr * size + nc) != player: break
            count += 1
            
        if count >= n_win:
            return True
    return False

def heuristic_rollout_policy(board):
    """
    Smart Policy:
    1. If I can win immediately -> Do it (100%).
    2. If opponent wins next turn -> Block it (100%).
    3. Otherwise -> Random.
    """
    availables = board.availables
    if not availables: return None
    
    current_p = board.current_player
    opp_p = 1 if current_p == 2 else 2
    size = board.width
    n_win = board.n_in_row
    
    # 1. Critical Offense: Can I win NOW?
    for move in availables:
        # We pass board.states directly to avoid slow object copying
        if check_win_local(board.states, move, current_p, size, n_win):
            return zip([move], [1.0])
            
    # 2. Critical Defense: Must I block?
    for move in availables:
        if check_win_local(board.states, move, opp_p, size, n_win):
            return zip([move], [1.0])

    # 3. Random
    probs = np.random.rand(len(availables))
    return zip(availables, probs)

class HeuristicMCTS(MCTS):
    def _evaluate_rollout(self, state, limit=1000):
        player = state.get_current_player()
        for i in range(limit):
            end, winner = state.game_end()
            if end: break
            
            # Use the optimized heuristic
            action_probs = heuristic_rollout_policy(state)
            max_action = max(action_probs, key=itemgetter(1))[0]
            
            state.do_move(max_action)
            
        if winner == -1: return 0
        return 1 if winner == player else -1

class HeuristicMCTSPlayer(MCTSPlayer):
    def __init__(self, c_puct=5, n_playout=400):
        # We override the internal MCTS instance with our Heuristic one
        self.mcts = HeuristicMCTS(self.dummy_policy, c_puct, n_playout)
        
    def dummy_policy(self, board):
        return zip(board.availables, np.ones(len(board.availables))/len(board.availables)), 0
        
    def get_action(self, board):
        if len(board.availables) > 0:
            move = self.mcts.get_move(board)
            self.mcts.update_with_move(-1)
            return move
        return -1
        
    def __str__(self): return "Heuristic MCTS"
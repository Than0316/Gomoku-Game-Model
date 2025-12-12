from GOMOKU_class_board import Board
from GOMOKU_evaluation_function import Evaluator, FIVE
from GOMOKU_move_generator import MoveGenerator
from GOMOKU_cache import Cache
from GOMOKU_config import Config

# Constants
MAX_SCORE = 1000000000
ONLY_THREE_THRESHOLD = 6

# Shared Cache
cache = Cache()
cache_hits = {'search': 0, 'total': 0, 'hit': 0}

def alpha_beta_factory(only_three=False, only_four=False):
    """
    Factory function to create specific searchers (Minimax, VCT, VCF).
    Returns a recursive helper function configured with specific filtering rules.
    """
    
    def search(board: Board, role: int, depth: int, current_depth=0, path=None, alpha=-MAX_SCORE, beta=MAX_SCORE):
        if path is None: path = []
        
        cache_hits['search'] += 1

        # 1. Base Case: Terminal State or Max Depth
        if current_depth >= depth or board.is_game_over()[0]:
            return [board.evaluator.evaluate(role), None, list(path)]

        # 2. Transposition Table Lookup
        hash_key = board.hash()
        prev = cache.get(hash_key)
        
        # Check if cache hit is valid
        if prev and prev['role'] == role:
            # We can use the cached result if:
            # A. It's a guaranteed win/loss (>= FIVE)
            # B. The cached depth is deeper or equal to what we need right now
            # C. The search constraints (onlyThree/onlyFour) match
            if (abs(prev['value']) >= FIVE or prev['depth'] >= depth - current_depth) and \
               prev['onlyThree'] == only_three and prev['onlyFour'] == only_four:
                cache_hits['hit'] += 1
                return [prev['value'], prev['move'], list(path) + prev['path']]

        # 3. Move Generation
        # Initialize generator if needed (assumes board has an evaluator attached)
        move_gen = MoveGenerator(board.evaluator)
        
        # Determine strictness of move generation
        is_strict_mode = only_three or (current_depth > ONLY_THREE_THRESHOLD)
        candidates = move_gen.get_moves(role, current_depth, is_strict_mode, only_four)

        if not candidates:
            return [board.evaluator.evaluate(role), None, list(path)]

        # 4. Iterative Deepening / Search Loop
        best_value = -MAX_SCORE
        best_move = None
        best_path = list(path)
        
        # In the JS code, Iterative Deepening (ID) happens here loop d = cDepth+1 to depth
        # We simplify to a standard DFS for clarity, as Python recursion depth is limited.
        
        for move in candidates:
            r, c = move
            
            # Execute Move
            board.put(r, c, role)
            board.evaluator.move(r, c, role)
            
            new_path = list(path) + [move]
            
            # Recursive Call (NegaMax: -beta becomes alpha, -alpha becomes beta)
            val, _, returned_path = search(board, -role, depth, current_depth + 1, new_path, -beta, -alpha)
            val = -val # Negate score from opponent's perspective
            
            # Undo Move
            board.evaluator.undo(r, c)
            board.undo()

            # --- Evaluation Logic ---
            
            # If we found a forced win, or if we are just searching normally
            if val >= FIVE:
                # Found a win, stop searching immediately (Aggressive pruning)
                best_value = val
                best_move = move
                best_path = returned_path
                break # Return immediately if we found a win
            
            # Update Best Move
            # Prefer wins with shorter paths, or delay losses with longer paths
            if (val > best_value) or \
               (val <= -FIVE and best_value <= -FIVE and len(returned_path) > len(best_path)):
                best_value = val
                best_move = move
                best_path = returned_path

            # Alpha-Beta Cutoff
            alpha = max(alpha, best_value)
            if alpha >= beta:
                break

        # 5. Cache Result
        # Only cache if we aren't in a super-shallow iterative deepening check
        # (Logic adapted from JS: checking specific thresholds)
        should_cache = (current_depth < ONLY_THREE_THRESHOLD or only_three or only_four)
        
        if should_cache:
            if not prev or prev['depth'] < depth - current_depth:
                cache_hits['total'] += 1
                cache.put(hash_key, {
                    'depth': depth - current_depth,
                    'value': best_value,
                    'move': best_move,
                    'role': role,
                    'path': best_path[current_depth:],
                    'onlyThree': only_three,
                    'onlyFour': only_four
                })

        return [best_value, best_move, best_path]

    return search

# --- Create the specific search functions ---
_minmax_search = alpha_beta_factory(only_three=False, only_four=False)
vct_search = alpha_beta_factory(only_three=True, only_four=False)
vcf_search = alpha_beta_factory(only_three=False, only_four=True)

# --- Main Entry Point ---
def minmax(board: Board, role: int, depth=4, enable_vct=True):
    """
    Main entry point for the AI.
    Combines VCT checks with standard Minimax search.
    """
    print(f"Thinking... (Role: {role}, Depth: {depth}, VCT: {enable_vct})")
    
    if enable_vct:
        vct_depth = depth + 8 # VCT searches deeper because moves are restricted
        
        # 1. Check if WE have a VCT win
        val, move, path = vct_search(board, role, vct_depth)
        if val >= FIVE:
            print(f"VCT Win Found! Path: {path}")
            return [val, move, path]
        
        # 2. If no VCT win, run standard Minimax
        val, move, path = _minmax_search(board, role, depth)
        
        # 3. Defense Check: Does the opponent have a VCT after our chosen move?
        # Logic: We simulate our best move, then check if opponent can kill us.
        if move:
            board.put(move[0], move[1], role)
            board.evaluator.move(move[0], move[1], role)
            
            # Check opponent's VCT threat on the resulting board
            val2, move2, path2 = vct_search(board, -role, vct_depth)
            
            board.evaluator.undo(move[0], move[1])
            board.undo()
            
            # If opponent has a win (val2 >= FIVE) despite our best move...
            # AND our current move didn't win immediately...
            # We try to find a better defensive move.
            if val < FIVE and val2 >= FIVE:
                print("Opponent has VCT threat! Attempting to block...")
                # (Simple block logic: usually handled by Minimax naturally, 
                # but explicit checks can be added here if needed).
                pass

        return [val, move, path]
    
    else:
        return _minmax_search(board, role, depth)
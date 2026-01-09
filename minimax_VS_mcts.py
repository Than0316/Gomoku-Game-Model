#!/usr/bin/env python3
"""
Compare Minimax vs MCTS strength from all openings:
  - Opening = (first move: center), (second move: any cell with Chebyshev distance <= 2 from center)
  - There are 25 cells in the 5x5 square around center; excluding the center gives 24 openings.

For each of those 24 openings we run two deterministic games (no randomness):
  A) Minimax starts first (Minimax = player 1), opening moves are applied (center, second)
  B) MCTS starts first (MCTS = player 1), opening moves are applied (center, second)

We then let the two AIs play deterministically to completion and record winners.
Outputs:
  - When Minimax starts first: Minimax win count / 24, MCTS win count, draws
  - When MCTS starts first: MCTS win count / 24, Minimax win count, draws

Usage:
  Place this file in the repo root (same level as EASY_GOMOKU/ and Monte_Carlo_guided_GOMOKU/)
  and run:
    python compare_strength_openings.py

Notes:
  - The script attempts to import modules robustly (package-style or top-level).
  - It assumes both AIs are deterministic (no sampling in MCTS rollout/final selection).
  - Minimax depth and MCTS playouts are configurable below.
"""

from pathlib import Path
import sys

# Make repo root and module folders importable regardless of invocation CWD
repo_root = Path(__file__).resolve().parent
sys.path.insert(0, str(repo_root))
sys.path.insert(0, str(repo_root / "EASY_GOMOKU"))
sys.path.insert(0, str(repo_root / "Monte_Carlo_guided_GOMOKU"))

# Try flexible imports (package-style first, then top-level)
try:
    from EASY_GOMOKU.EASY_GOMOKU_class_board import Board as EasyBoard
except Exception:
    try:
        from EASY_GOMOKU_class_board import Board as EasyBoard
    except Exception as e:
        raise ImportError("Could not import EASY_GOMOKU_class_board") from e

try:
    from EASY_GOMOKU.EASY_GOMOKU_minimax import find_best_move
except Exception:
    try:
        from EASY_GOMOKU_minimax import find_best_move
    except Exception as e:
        raise ImportError("Could not import EASY_GOMOKU_minimax.find_best_move") from e

try:
    from Monte_Carlo_guided_GOMOKU.mcts_game import Board as MCTSBoard
except Exception:
    try:
        from mcts_game import Board as MCTSBoard
    except Exception as e:
        raise ImportError("Could not import Monte_Carlo_guided_GOMOKU.mcts_game.Board") from e

try:
    from Monte_Carlo_guided_GOMOKU.mcts_guided import MCTSPlayer
except Exception:
    try:
        from mcts_guided import MCTSPlayer
    except Exception as e:
        raise ImportError("Could not import Monte_Carlo_guided_GOMOKU.mcts_guided.MCTSPlayer") from e

# Configuration for strength comparison (deterministic)
MINIMAX_DEPTH = 3     # depth used by Minimax evaluation
MCTS_PLAYOUTS = 400   # number of playouts used by MCTS get_action (deterministic if implementation is deterministic)

# Helpers
def rc_to_idx(r, c, size):
    return int(r) * int(size) + int(c)

def idx_to_rc(idx, size):
    return divmod(int(idx), int(size))

def center_index(size):
    # EASY_GOMOKU used center = SIZE//2 - 1
    center = size // 2 - 1
    return rc_to_idx(center, center, size)

def within_chebyshev(a_idx, b_idx, size, max_dist=2):
    ar, ac = idx_to_rc(a_idx, size)
    br, bc = idx_to_rc(b_idx, size)
    return max(abs(ar - br), abs(ac - bc)) <= max_dist

def all_valid_second_moves(size, max_dist=2):
    cidx = center_index(size)
    moves = []
    for r in range(size):
        for c in range(size):
            idx = rc_to_idx(r, c, size)
            if idx == cidx:
                continue
            if within_chebyshev(cidx, idx, size, max_dist=max_dist):
                moves.append(idx)
    return moves

def construct_fresh_mcts_board(size, n_in_row):
    b = MCTSBoard(width=size, height=size, n_in_row=n_in_row)
    b.init_board(start_player=0)
    return b

def construct_fresh_easy_board():
    # Attempt to construct either new-style or old-style EasyBoard
    try:
        eb = EasyBoard(states=None, current_player=1)
    except TypeError:
        # older signature likely Board(player='X')
        eb = EasyBoard(player='X')
    return eb

def apply_opening_moves(easy_board, mcts_board, first_idx, second_idx):
    """
    Apply two fixed opening moves (first_idx then second_idx) to both boards.
    Both indices are flat indices and moves are applied in that order.
    Returns (easy_board_after_opening, mcts_board_after_opening)
    """
    # EasyBoard.play may accept flat index (converted repository) or (r,c) tuple (older).
    eb = easy_board
    try:
        eb = eb.play(first_idx)
    except Exception:
        r, c = idx_to_rc(first_idx, eb.SIZE)
        eb = eb.play((r, c))
    try:
        eb = eb.play(second_idx)
    except Exception:
        r2, c2 = idx_to_rc(second_idx, eb.SIZE)
        eb = eb.play((r2, c2))

    # MCTS board in-place
    mcts_board.do_move(first_idx)
    mcts_board.do_move(second_idx)
    return eb, mcts_board

def play_deterministic_game_from(open_easy_board, open_mcts_board, minimax_player, minimax_depth, mcts_playouts):
    """
    Play deterministically to completion starting from the provided opening boards.
    Returns winner: 1 or 2 for players, -1 for draw
    """
    # Create a fresh MCTS player for this game (fresh tree)
    mcts_player = MCTSPlayer(c_puct=5, n_playout=mcts_playouts)

    easy_board = open_easy_board
    mcts_board = open_mcts_board

    # helper to normalize move formats to flat index
    def normalize_move(move, size):
        # move may be int, or (r, c) tuple/list, or maybe numpy types
        if move is None:
            return None
        if isinstance(move, (tuple, list)):
            r, c = int(move[0]), int(move[1])
            return rc_to_idx(r, c, size)
        # some functions may return numpy.int64 etc. int(...) will handle real numbers
        try:
            return int(move)
        except Exception:
            # last fallback: if it's a string like "r,c"
            if isinstance(move, str) and ',' in move:
                parts = [int(x) for x in move.split(',')]
                return rc_to_idx(parts[0], parts[1], size)
            raise

    size = EasyBoard.SIZE

    # play until end
    while True:
        end, winner = mcts_board.game_end()
        if end:
            return winner

        current = mcts_board.get_current_player()
        if current == minimax_player:
            # Minimax turn
            try:
                move = find_best_move(easy_board, depth=minimax_depth)
            except TypeError:
                move = find_best_move(easy_board)
            move_idx = normalize_move(move, size)
            if move_idx is None:
                return -1
        else:
            # MCTS turn (deterministic call)
            try:
                move_candidate = mcts_player.get_action(mcts_board, temp=0)
            except TypeError:
                move_candidate = mcts_player.get_action(mcts_board)
            # get_action may return (move, probs) or move
            if isinstance(move_candidate, (tuple, list)):
                move_raw = move_candidate[0]
            else:
                move_raw = move_candidate
            move_idx = normalize_move(move_raw, size)

        # Apply the move to both boards
        # to easy_board
        try:
            easy_board = easy_board.play(move_idx)
        except Exception:
            # fallback to (r,c)
            r, c = idx_to_rc(move_idx, easy_board.SIZE)
            easy_board = easy_board.play((r, c))

        # to mcts_board (in-place)
        mcts_board.do_move(move_idx)

        # Reset MCTS player's root so tree is not reused across changed root
        try:
            mcts_player.reset_player()
        except Exception:
            pass

def run_all_openings_and_compare(minimax_depth=MINIMAX_DEPTH, mcts_playouts=MCTS_PLAYOUTS):
    size = EasyBoard.SIZE
    n_in_row = getattr(EasyBoard, "N_IN_ROW", 4)
    center_idx = center_index(size)
    second_moves = all_valid_second_moves(size, max_dist=2)  # 24 moves

    # Counters for the two experiments:
    # when Minimax starts first (Minimax = player 1)
    minimax_first_results = {"minimax_wins": 0, "mcts_wins": 0, "draws": 0}
    # when MCTS starts first (MCTS = player 1)
    mcts_first_results = {"mcts_wins": 0, "minimax_wins": 0, "draws": 0}

    # iterate all second moves
    for second_idx in second_moves:
        # 1) Minimax starts first: Minimax is player 1, opening moves are center (p1) and second (p2)
        # construct fresh boards
        easy_init = construct_fresh_easy_board()
        mcts_init = construct_fresh_mcts_board(size, n_in_row)
        # apply opening: center then second (positions fixed)
        open_easy, open_mcts = apply_opening_moves(easy_init, mcts_init, center_idx, second_idx)
        # play game deterministically with Minimax as player 1
        winner = play_deterministic_game_from(open_easy, open_mcts, minimax_player=1,
                                              minimax_depth=minimax_depth, mcts_playouts=mcts_playouts)
        if winner == -1:
            minimax_first_results["draws"] += 1
        elif winner == 1:
            minimax_first_results["minimax_wins"] += 1
        else:
            minimax_first_results["mcts_wins"] += 1

        # 2) MCTS starts first: MCTS is player 1, opening moves are still center (p1) and second (p2)
        easy_init = construct_fresh_easy_board()
        mcts_init = construct_fresh_mcts_board(size, n_in_row)
        open_easy, open_mcts = apply_opening_moves(easy_init, mcts_init, center_idx, second_idx)
        # play game deterministically with Minimax as player 2 (i.e., MCTS=player1)
        winner = play_deterministic_game_from(open_easy, open_mcts, minimax_player=2,
                                              minimax_depth=minimax_depth, mcts_playouts=mcts_playouts)
        if winner == -1:
            mcts_first_results["draws"] += 1
        elif winner == 2:
            mcts_first_results["minimax_wins"] += 1  # winner==2 means Minimax (player2) won
        else:
            mcts_first_results["mcts_wins"] += 1

    # Print summary
    total_openings = len(second_moves)
    print("\n=== RESULTS OVER ALL OPENINGS ===")
    print(f"Total openings tested: {total_openings} (center + each of {total_openings} second moves)\n")

    print("Case A: Minimax starts first (Minimax = player 1)")
    print(f"  Minimax wins: {minimax_first_results['minimax_wins']} / {total_openings} "
          f"({minimax_first_results['minimax_wins'] / total_openings:.2%})")
    print(f"  MCTS wins:    {minimax_first_results['mcts_wins']} / {total_openings} "
          f"({minimax_first_results['mcts_wins'] / total_openings:.2%})")
    print(f"  Draws:        {minimax_first_results['draws']} / {total_openings} "
          f"({minimax_first_results['draws'] / total_openings:.2%})\n")

    print("Case B: MCTS starts first (MCTS = player 1)")
    print(f"  MCTS wins:    {mcts_first_results['mcts_wins']} / {total_openings} "
          f"({mcts_first_results['mcts_wins'] / total_openings:.2%})")
    print(f"  Minimax wins: {mcts_first_results['minimax_wins']} / {total_openings} "
          f"({mcts_first_results['minimax_wins'] / total_openings:.2%})")
    print(f"  Draws:        {mcts_first_results['draws']} / {total_openings} "
          f"({mcts_first_results['draws'] / total_openings:.2%})\n")

    return minimax_first_results, mcts_first_results

if __name__ == "__main__":
    print("Running deterministic strength comparison over all valid second moves around center...")
    run_all_openings_and_compare()

"""
=== RESULTS OVER ALL OPENINGS ===
Total openings tested: 24 (center + each of 24 second moves)

Case A: Minimax starts first (Minimax = player 1)
  Minimax wins: 4 / 24 (16.67%)
  MCTS wins:    20 / 24 (83.33%)
  Draws:        0 / 24 (0.00%)

Case B: MCTS starts first (MCTS = player 1)
  MCTS wins:    23 / 24 (95.83%)
  Minimax wins: 1 / 24 (4.17%)
  Draws:        0 / 24 (0.00%)
"""
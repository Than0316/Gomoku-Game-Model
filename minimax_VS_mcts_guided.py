#!/usr/bin/env python3
"""
Compare Minimax vs MCTS strength from all openings with timing and progress bar.
"""

from pathlib import Path
import sys
from tqdm import tqdm
import time
import numpy as np

# Make repo root and module folders importable regardless of invocation CWD
repo_root = Path(__file__).resolve().parent
sys.path.insert(0, str(repo_root))
sys.path.insert(0, str(repo_root / "EASY_GOMOKU"))
sys.path.insert(0, str(repo_root / "Monte_Carlo_guided_GOMOKU"))

# Flexible imports
try:
    from EASY_GOMOKU.EASY_GOMOKU_class_board import Board as EasyBoard
except Exception:
    from EASY_GOMOKU_class_board import Board as EasyBoard

try:
    from EASY_GOMOKU.EASY_GOMOKU_minimax import find_best_move
except Exception:
    from EASY_GOMOKU_minimax import find_best_move

try:
    from Monte_Carlo_guided_GOMOKU.mcts_game import Board as MCTSBoard
except Exception:
    from mcts_game import Board as MCTSBoard

try:
    from Monte_Carlo_guided_GOMOKU.mcts_guided import MCTSPlayer
except Exception:
    from mcts_guided import MCTSPlayer

# Configuration
MINIMAX_DEPTH = 3
MCTS_PLAYOUTS = 400

# ------------------ Helpers ------------------
def rc_to_idx(r, c, size):
    return int(r) * int(size) + int(c)

def idx_to_rc(idx, size):
    return divmod(int(idx), int(size))

def center_index(size):
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
    try:
        eb = EasyBoard(states=None, current_player=1)
    except TypeError:
        eb = EasyBoard(player='X')
    return eb

def apply_opening_moves(easy_board, mcts_board, first_idx, second_idx):
    try:
        easy_board = easy_board.play(first_idx)
    except Exception:
        r, c = idx_to_rc(first_idx, easy_board.SIZE)
        easy_board = easy_board.play((r, c))
    try:
        easy_board = easy_board.play(second_idx)
    except Exception:
        r2, c2 = idx_to_rc(second_idx, easy_board.SIZE)
        easy_board = easy_board.play((r2, c2))

    mcts_board.do_move(first_idx)
    mcts_board.do_move(second_idx)
    return easy_board, mcts_board

# ------------------ Timed Game Play ------------------
def play_deterministic_game_from_timed(open_easy_board, open_mcts_board, minimax_player,
                                       minimax_depth, mcts_playouts, minimax_times, mcts_times):
    mcts_player = MCTSPlayer(c_puct=5, n_playout=mcts_playouts)
    easy_board = open_easy_board
    mcts_board = open_mcts_board
    size = EasyBoard.SIZE

    def normalize_move(move, size):
        if move is None:
            return None
        if isinstance(move, (tuple, list)):
            r, c = int(move[0]), int(move[1])
            return rc_to_idx(r, c, size)
        try:
            return int(move)
        except Exception:
            if isinstance(move, str) and ',' in move:
                parts = [int(x) for x in move.split(',')]
                return rc_to_idx(parts[0], parts[1], size)
            raise

    while True:
        end, winner = mcts_board.game_end()
        if end:
            return winner

        current = mcts_board.get_current_player()
        if current == minimax_player:
            start = time.perf_counter()
            try:
                move = find_best_move(easy_board, depth=minimax_depth)
            except TypeError:
                move = find_best_move(easy_board)
            elapsed = time.perf_counter() - start
            minimax_times.append(elapsed)
            move_idx = normalize_move(move, size)
            if move_idx is None:
                return -1
        else:
            start = time.perf_counter()
            try:
                move_candidate = mcts_player.get_action(mcts_board, temp=0)
            except TypeError:
                move_candidate = mcts_player.get_action(mcts_board)
            elapsed = time.perf_counter() - start
            mcts_times.append(elapsed)
            move_idx = move_candidate[0] if isinstance(move_candidate, (tuple, list)) else move_candidate
            move_idx = normalize_move(move_idx, size)

        try:
            easy_board = easy_board.play(move_idx)
        except Exception:
            r, c = idx_to_rc(move_idx, easy_board.SIZE)
            easy_board = easy_board.play((r, c))
        mcts_board.do_move(move_idx)
        try:
            mcts_player.reset_player()
        except Exception:
            pass

# ------------------ Main Comparison ------------------
def run_all_openings_and_compare(minimax_depth=MINIMAX_DEPTH, mcts_playouts=MCTS_PLAYOUTS):
    size = EasyBoard.SIZE
    n_in_row = getattr(EasyBoard, "N_IN_ROW", 4)
    center_idx = center_index(size)
    second_moves = all_valid_second_moves(size, max_dist=2)

    minimax_first_results = {"minimax_wins": 0, "mcts_wins": 0, "draws": 0}
    mcts_first_results = {"mcts_wins": 0, "minimax_wins": 0, "draws": 0}

    minimax_times = []
    mcts_times = []

    start_total = time.perf_counter()

    for second_idx in tqdm(second_moves, desc="Opening moves"):
        for is_minimax_first in [True, False]:
            easy_init = construct_fresh_easy_board()
            mcts_init = construct_fresh_mcts_board(size, n_in_row)
            open_easy, open_mcts = apply_opening_moves(easy_init, mcts_init, center_idx, second_idx)

            minimax_player = 1 if is_minimax_first else 2

            winner = play_deterministic_game_from_timed(
                open_easy, open_mcts, minimax_player,
                minimax_depth=minimax_depth, mcts_playouts=mcts_playouts,
                minimax_times=minimax_times, mcts_times=mcts_times
            )

            if is_minimax_first:
                if winner == -1:
                    minimax_first_results["draws"] += 1
                elif winner == 1:
                    minimax_first_results["minimax_wins"] += 1
                else:
                    minimax_first_results["mcts_wins"] += 1
            else:
                if winner == -1:
                    mcts_first_results["draws"] += 1
                elif winner == 2:
                    mcts_first_results["minimax_wins"] += 1
                else:
                    mcts_first_results["mcts_wins"] += 1

    end_total = time.perf_counter()
    total_runtime = end_total - start_total

    # Print results
    print(f"\n=== TOTAL RUNTIME: {total_runtime:.2f} s ===")
    print(f"Average Minimax decision time: {np.mean(minimax_times)*1000:.2f} ms")
    print(f"Average MCTS decision time:    {np.mean(mcts_times)*1000:.2f} ms\n")

    total_openings = len(second_moves)
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

# ------------------ Main ------------------
if __name__ == "__main__":
    print("Running deterministic strength comparison over all valid second moves around center...")
    run_all_openings_and_compare()

"""
=== TOTAL RUNTIME: 160.43 s ===
Average Minimax decision time: 302.64 ms
Average MCTS decision time:    181.04 ms

Case A: Minimax starts first (Minimax = player 1)
  Minimax wins: 1 / 24 (4.17%)
  MCTS wins:    23 / 24 (95.83%)
  Draws:        0 / 24 (0.00%)

Case B: MCTS starts first (MCTS = player 1)
  MCTS wins:    24 / 24 (100.00%)
  Minimax wins: 0 / 24 (0.00%)
  Draws:        0 / 24 (0.00%)
"""
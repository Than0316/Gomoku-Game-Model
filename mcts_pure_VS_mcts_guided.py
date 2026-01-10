#!/usr/bin/env python3
"""
Compare MCTS Pure vs MCTS Guided strength from all openings with timing and progress bar.
"""

from pathlib import Path
import sys
from tqdm import tqdm
import time
import numpy as np

# Make repo root and module folders importable
repo_root = Path(__file__).resolve().parent
sys.path.insert(0, str(repo_root))
sys.path.insert(0, str(repo_root / "Monte_Carlo_guided_GOMOKU"))

# Flexible imports
try:
    from Monte_Carlo_guided_GOMOKU.mcts_game import Board as MCTSBoard
except Exception:
    from mcts_game import Board as MCTSBoard

try:
    from Monte_Carlo_guided_GOMOKU.mcts_pure import MCTSPlayer as MCTSPlayerPure
except Exception:
    from mcts_pure import MCTSPlayer as MCTSPlayerPure

try:
    from Monte_Carlo_guided_GOMOKU.mcts_guided import MCTSPlayer as MCTSPlayerGuided
except Exception:
    from mcts_guided import MCTSPlayer as MCTSPlayerGuided

# ------------------ Configuration ------------------
N_PLAYOUTS = 400

# ------------------ Helpers ------------------
def rc_to_idx(r, c, size):
    return r * size + c

def idx_to_rc(idx, size):
    return divmod(idx, size)

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

def construct_fresh_board(size, n_in_row):
    b = MCTSBoard(width=size, height=size, n_in_row=n_in_row)
    b.init_board(start_player=1)
    return b

def apply_opening_moves(board, first_idx, second_idx):
    board.do_move(first_idx)
    board.do_move(second_idx)
    return board

# ------------------ Timed MCTS Game ------------------
def play_mcts_vs_mcts(board, first_is_pure=True, n_playouts=N_PLAYOUTS):
    if first_is_pure:
        players = {1: MCTSPlayerPure(c_puct=5, n_playout=n_playouts),
                   2: MCTSPlayerGuided(c_puct=5, n_playout=n_playouts)}
    else:
        players = {1: MCTSPlayerGuided(c_puct=5, n_playout=n_playouts),
                   2: MCTSPlayerPure(c_puct=5, n_playout=n_playouts)}

    move_times = {1: [], 2: []}

    while True:
        end, winner = board.game_end()
        if end:
            return winner, move_times

        current = board.get_current_player()
        start = time.perf_counter()
        move = players[current].get_action(board)  # Pure or Guided
        elapsed = time.perf_counter() - start
        move_times[current].append(elapsed)

        move_idx = move[0] if isinstance(move, (tuple, list)) else move
        board.do_move(move_idx)

        # reset search trees if needed
        for p in players.values():
            try:
                p.reset_player()
            except Exception:
                pass

# ------------------ Main Comparison ------------------
def run_all_openings_vs_mcts(size=8, n_in_row=4, n_playouts=N_PLAYOUTS, max_dist=2):
    center_idx = center_index(size)
    second_moves = all_valid_second_moves(size, max_dist=max_dist)

    pure_first_results = {"pure_wins": 0, "guided_wins": 0, "draws": 0}
    guided_first_results = {"guided_wins": 0, "pure_wins": 0, "draws": 0}

    pure_times, guided_times = [], []

    start_total = time.perf_counter()

    for second_idx in tqdm(second_moves, desc="Opening moves"):
        for is_pure_first in [True, False]:
            board = construct_fresh_board(size, n_in_row)
            apply_opening_moves(board, center_idx, second_idx)

            winner, move_times = play_mcts_vs_mcts(board, first_is_pure=is_pure_first, n_playouts=n_playouts)

            if is_pure_first:
                pure_times.extend(move_times[1])
                guided_times.extend(move_times[2])
                if winner == 1:
                    pure_first_results["pure_wins"] += 1
                elif winner == 2:
                    pure_first_results["guided_wins"] += 1
                else:
                    pure_first_results["draws"] += 1
            else:
                guided_times.extend(move_times[1])
                pure_times.extend(move_times[2])
                if winner == 1:
                    guided_first_results["guided_wins"] += 1
                elif winner == 2:
                    guided_first_results["pure_wins"] += 1
                else:
                    guided_first_results["draws"] += 1

    total_runtime = time.perf_counter() - start_total

    # Print results
    print(f"\n=== TOTAL RUNTIME: {total_runtime:.2f} s ===")
    print(f"Average Pure MCTS move time:   {np.mean(pure_times)*1000:.2f} ms")
    print(f"Average Guided MCTS move time: {np.mean(guided_times)*1000:.2f} ms\n")

    total_openings = len(second_moves)
    print("Case A: Pure MCTS starts first (Pure = player 1)")
    print(f"  Pure wins:    {pure_first_results['pure_wins']} / {total_openings} "
          f"({pure_first_results['pure_wins']/total_openings:.2%})")
    print(f"  Guided wins:  {pure_first_results['guided_wins']} / {total_openings} "
          f"({pure_first_results['guided_wins']/total_openings:.2%})")
    print(f"  Draws:        {pure_first_results['draws']} / {total_openings} "
          f"({pure_first_results['draws']/total_openings:.2%})\n")

    print("Case B: Guided MCTS starts first (Guided = player 1)")
    print(f"  Guided wins:  {guided_first_results['guided_wins']} / {total_openings} "
          f"({guided_first_results['guided_wins']/total_openings:.2%})")
    print(f"  Pure wins:    {guided_first_results['pure_wins']} / {total_openings} "
          f"({guided_first_results['pure_wins']/total_openings:.2%})")
    print(f"  Draws:        {guided_first_results['draws']} / {total_openings} "
          f"({guided_first_results['draws']/total_openings:.2%})\n")

    return pure_first_results, guided_first_results

# ------------------ Main ------------------
if __name__ == "__main__":
    print("Running deterministic strength comparison over all valid second moves around center...")
    run_all_openings_vs_mcts()

"""
=== TOTAL RUNTIME: 140.63 s ===
Average Pure MCTS move time:   228.57 ms
Average Guided MCTS move time: 234.45 ms

Case A: Pure MCTS starts first (Pure = player 1)
  Pure wins:    3 / 24 (12.50%)
  Guided wins:  21 / 24 (87.50%)
  Draws:        0 / 24 (0.00%)

Case B: Guided MCTS starts first (Guided = player 1)
  Guided wins:  16 / 24 (66.67%)
  Pure wins:    8 / 24 (33.33%)
  Draws:        0 / 24 (0.00%)
"""
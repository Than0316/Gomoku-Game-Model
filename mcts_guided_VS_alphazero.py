#!/usr/bin/env python3
"""
Compare AlphaZero-guided MCTS vs Guided MCTS over all openings, timing each move, with progress bar.
"""

from pathlib import Path
import sys
from tqdm import tqdm
import time
import numpy as np
import pickle

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
    from Monte_Carlo_guided_GOMOKU.mcts_guided import MCTSPlayer as GuidedMCTS
except Exception:
    from mcts_guided import MCTSPlayer as GuidedMCTS

try:
    from Monte_Carlo_guided_GOMOKU.mcts_alphaZero import MCTSPlayer as AlphaZeroMCTS
    from Monte_Carlo_guided_GOMOKU.policy_value_net_numpy import PolicyValueNetNumpy
except Exception:
    from mcts_alphaZero import MCTSPlayer as AlphaZeroMCTS
    from policy_value_net_numpy import PolicyValueNetNumpy

# Configuration
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

def construct_fresh_board(size, n_in_row):
    b = MCTSBoard(width=size, height=size, n_in_row=n_in_row)
    b.init_board(start_player=0)
    return b

# ------------------ Timed Game Play ------------------
def play_alphazero_vs_guided(board_init, first_is_alpha=True, n_playouts=MCTS_PLAYOUTS):
    size = board_init.width
    board = board_init

    # --- AlphaZero policy-value network ---
    model_file = repo_root / "Monte_Carlo_guided_GOMOKU" / "best_policy_6_6_4.model"
    with open(model_file, 'rb') as f:
        policy_param = pickle.load(f, encoding='latin1')

    best_policy = PolicyValueNetNumpy(board_width=size, board_height=size, net_params=policy_param)
    policy_fn = best_policy.policy_value_fn

    # --- Players ---
    player_map = {
        1: AlphaZeroMCTS(policy_fn, c_puct=5, n_playout=n_playouts) if first_is_alpha else GuidedMCTS(c_puct=5, n_playout=n_playouts),
        2: GuidedMCTS(c_puct=5, n_playout=n_playouts) if first_is_alpha else AlphaZeroMCTS(policy_fn, c_puct=5, n_playout=n_playouts)
    }

    move_times = {1: [], 2: []}

    while True:
        end, winner = board.game_end()
        if end:
            avg_times = {p: np.mean(times)*1000 if times else 0 for p, times in move_times.items()}
            return winner, avg_times

        current = board.get_current_player()
        player = player_map[current]

        start = time.perf_counter()
        try:
            move = player.get_action(board, temp=1e-3)
        except TypeError:
            move = player.get_action(board)
        elapsed = time.perf_counter() - start
        move_times[current].append(elapsed)

        move_idx = move[0] if isinstance(move, (tuple, list)) else move
        board.do_move(move_idx)

        try:
            player.reset_player()
        except Exception:
            pass

# ------------------ Main Comparison ------------------
def run_all_openings_vs_alpha_and_guided(n_playouts=MCTS_PLAYOUTS):
    size = 6
    n_in_row = 4
    center_idx = center_index(size)
    second_moves = all_valid_second_moves(size, max_dist=2)

    alpha_first_results = {"alpha_wins": 0, "guided_wins": 0, "draws": 0, "alpha_times": [], "guided_times": []}
    guided_first_results = {"alpha_wins": 0, "guided_wins": 0, "draws": 0, "alpha_times": [], "guided_times": []}

    start_total = time.perf_counter()

    for second_idx in tqdm(second_moves, desc="Opening moves"):
        for is_alpha_first in [True, False]:
            board = construct_fresh_board(size, n_in_row)
            board.do_move(center_idx)
            board.do_move(second_idx)

            winner, avg_times = play_alphazero_vs_guided(board, first_is_alpha=is_alpha_first, n_playouts=n_playouts)

            if is_alpha_first:
                alpha_first_results["alpha_times"].append(avg_times[1])
                alpha_first_results["guided_times"].append(avg_times[2])
                if winner == -1:
                    alpha_first_results["draws"] += 1
                elif winner == 1:
                    alpha_first_results["alpha_wins"] += 1
                else:
                    alpha_first_results["guided_wins"] += 1
            else:
                guided_first_results["alpha_times"].append(avg_times[2])
                guided_first_results["guided_times"].append(avg_times[1])
                if winner == -1:
                    guided_first_results["draws"] += 1
                elif winner == 2:
                    guided_first_results["alpha_wins"] += 1
                else:
                    guided_first_results["guided_wins"] += 1

    end_total = time.perf_counter()
    total_runtime = end_total - start_total

    # --- Print results ---
    print(f"\n=== TOTAL RUNTIME: {total_runtime:.2f} s ===")
    print(f"Average AlphaZero game time: {np.mean(alpha_first_results['alpha_times'] + guided_first_results['alpha_times']):.2f} ms")
    print(f"Average Guided MCTS game time: {np.mean(alpha_first_results['guided_times'] + guided_first_results['guided_times']):.2f} ms\n")

    total_openings = len(second_moves)
    print("Case A: AlphaZero starts first (AlphaZero = player 1)")
    print(f"  AlphaZero wins: {alpha_first_results['alpha_wins']} / {total_openings} "
          f"({alpha_first_results['alpha_wins'] / total_openings:.2%})")
    print(f"  Guided wins:    {alpha_first_results['guided_wins']} / {total_openings} "
          f"({alpha_first_results['guided_wins'] / total_openings:.2%})")
    print(f"  Draws:          {alpha_first_results['draws']} / {total_openings} "
          f"({alpha_first_results['draws'] / total_openings:.2%})\n")

    print("Case B: Guided MCTS starts first (Guided = player 1)")
    print(f"  Guided wins:    {guided_first_results['guided_wins']} / {total_openings} "
          f"({guided_first_results['guided_wins'] / total_openings:.2%})")
    print(f"  AlphaZero wins: {guided_first_results['alpha_wins']} / {total_openings} "
          f"({guided_first_results['alpha_wins'] / total_openings:.2%})")
    print(f"  Draws:          {guided_first_results['draws']} / {total_openings} "
          f"({guided_first_results['draws'] / total_openings:.2%})\n")

    return alpha_first_results, guided_first_results

# ------------------ Main ------------------
if __name__ == "__main__":
    print("Running deterministic strength comparison over all valid second moves around center...")
    run_all_openings_vs_alpha_and_guided()

"""
=== TOTAL RUNTIME: 137.05 s ===
Average AlphaZero game time: 440.37 ms
Average Guided MCTS game time: 282.89 ms

Case A: AlphaZero starts first (AlphaZero = player 1)
  AlphaZero wins: 24 / 24 (100.00%)
  Guided wins:    0 / 24 (0.00%)
  Draws:          0 / 24 (0.00%)

Case B: Guided MCTS starts first (Guided = player 1)
  Guided wins:    15 / 24 (62.50%)
  AlphaZero wins: 9 / 24 (37.50%)
  Draws:          0 / 24 (0.00%)
"""
#!/usr/bin/env python3
from pathlib import Path
import sys, time, numpy as np
from tqdm import tqdm

repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))
sys.path.insert(0, str(repo_root / "mcts"))

from mcts.game import Board as MCTSBoard
from mcts.mcts_pure import MCTSPlayer as MCTSPure
from mcts.mcts_heuristic import HeuristicMCTSPlayer

MCTS_PLAYOUTS, SIZE, N_IN_ROW, MAX_DIST = 200, 8, 5, 1

def rc_to_idx(r, c, s): return int(r) * int(s) + int(c)
def center_index(s): return rc_to_idx(s // 2 - 1, s // 2 - 1, s)
def idx_to_rc(i, s): return divmod(int(i), int(s))
def within_chebyshev(a, b, size, dist):
    ar, ac = idx_to_rc(a, size); br, bc = idx_to_rc(b, size)
    return max(abs(ar - br), abs(ac - bc)) <= dist
def all_valid_second_moves(size, max_dist):
    c = center_index(size); moves = []
    for i in range(size*size):
        if i != c and within_chebyshev(c, i, size, max_dist): moves.append(i)
    return moves

def play_match(board_init, first_is_p1):
    board = board_init
    # P1 = Pure, P2 = Heuristic
    p1 = MCTSPure(n_playout=MCTS_PLAYOUTS)
    p2 = HeuristicMCTSPlayer(n_playout=MCTS_PLAYOUTS)
    player_map = {1: p1 if first_is_p1 else p2, 2: p2 if first_is_p1 else p1}
    move_times = {1: [], 2: []}

    while True:
        end, winner = board.game_end()
        if end:
            w_agent = None
            if winner != -1:
                if first_is_p1: w_agent = "Pure" if winner == 1 else "Heur"
                else: w_agent = "Pure" if winner == 2 else "Heur"
            
            t1 = np.mean(move_times[1])*1000 if move_times[1] else 0
            t2 = np.mean(move_times[2])*1000 if move_times[2] else 0
            times = {"Pure": t1 if first_is_p1 else t2, "Heur": t2 if first_is_p1 else t1}
            return w_agent, times

        curr = board.get_current_player()
        player = player_map[curr]
        st = time.perf_counter()
        move = player.get_action(board)
        move_times[curr].append(time.perf_counter() - st)
        board.do_move(move)
        if hasattr(player, 'reset_player'): player.reset_player()

def run():
    center = center_index(SIZE)
    second_moves = all_valid_second_moves(SIZE, MAX_DIST)
    
    case_a = {"Pure": 0, "Heur": 0, "Draws": 0}
    case_b = {"Pure": 0, "Heur": 0, "Draws": 0}
    all_times = {"Pure": [], "Heur": []}

    print(f"Starting: Pure MCTS vs Heuristic MCTS ({len(second_moves)*2} games)")
    start_total = time.time()

    for second_idx in tqdm(second_moves):
        # Case A
        b = MCTSBoard(width=SIZE, height=SIZE, n_in_row=N_IN_ROW)
        b.init_board(start_player=0); b.do_move(center); b.do_move(second_idx)
        w, t = play_match(b, True)
        all_times["Pure"].append(t["Pure"]); all_times["Heur"].append(t["Heur"])
        if w == "Pure": case_a["Pure"] += 1
        elif w == "Heur": case_a["Heur"] += 1
        else: case_a["Draws"] += 1

        # Case B
        b = MCTSBoard(width=SIZE, height=SIZE, n_in_row=N_IN_ROW)
        b.init_board(start_player=0); b.do_move(center); b.do_move(second_idx)
        w, t = play_match(b, False)
        all_times["Pure"].append(t["Pure"]); all_times["Heur"].append(t["Heur"])
        if w == "Pure": case_b["Pure"] += 1
        elif w == "Heur": case_b["Heur"] += 1
        else: case_b["Draws"] += 1

    total_time = time.time() - start_total
    tot = len(second_moves)

    print(f"\n=== TOTAL RUNTIME: {total_time:.2f} s ===")
    print(f"Average Pure MCTS decision time: {np.mean(all_times['Pure']):.2f} ms")
    print(f"Average Heuristic MCTS decision time: {np.mean(all_times['Heur']):.2f} ms\n")

    print(f"Case A: Pure MCTS starts first")
    print(f"  Pure wins:    {case_a['Pure']} / {tot} ({case_a['Pure']/tot:.2%})")
    print(f"  Heur MCTS wins:    {case_a['Heur']} / {tot} ({case_a['Heur']/tot:.2%})")
    print(f"  Draws:        {case_a['Draws']} / {tot} ({case_a['Draws']/tot:.2%})\n")

    print(f"Case B: Heuristic MCTS starts first")
    print(f"  Heur MCTS wins:    {case_b['Heur']} / {tot} ({case_b['Heur']/tot:.2%})")
    print(f"  Pure wins:    {case_b['Pure']} / {tot} ({case_b['Pure']/tot:.2%})")
    print(f"  Draws:        {case_b['Draws']} / {tot} ({case_b['Draws']/tot:.2%})\n")

if __name__ == "__main__": run()

"""
=== TOTAL RUNTIME: 517.81 s ===
Average Pure MCTS decision time: 728.76 ms
Average Heuristic MCTS decision time: 1897.41 ms

Case A: Pure MCTS starts first
  Pure wins:    3 / 8 (37.50%)
  Heur MCTS wins:    5 / 8 (62.50%)
  Draws:        0 / 8 (0.00%)

Case B: Heuristic MCTS starts first
  Heur MCTS wins:    6 / 8 (75.00%)
  Pure wins:    1 / 8 (12.50%)
  Draws:        1 / 8 (12.50%)

"""
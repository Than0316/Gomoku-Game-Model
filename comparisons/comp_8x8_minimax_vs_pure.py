#!/usr/bin/env python3
from pathlib import Path
import sys, time, numpy as np
from tqdm import tqdm

repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))
sys.path.insert(0, str(repo_root / "mcts"))

from mcts.game import Board as MCTSBoard
from mcts.mcts_pure import MCTSPlayer as MCTSPure
from Gomoku_8_8.minimax_adapter import MinimaxPlayer

MCTS_PLAYOUTS = 200
SIZE, N_IN_ROW, MAX_DIST = 8, 5, 1

def rc_to_idx(r, c, s): return int(r) * int(s) + int(c)
def idx_to_rc(i, s): return divmod(int(i), int(s))
def center_index(s): return rc_to_idx(s // 2 - 1, s // 2 - 1, s)
def within_chebyshev(a, b, size, dist):
    ar, ac = idx_to_rc(a, size); br, bc = idx_to_rc(b, size)
    return max(abs(ar - br), abs(ac - bc)) <= dist
def all_valid_second_moves(size, max_dist):
    c = center_index(size); moves = []
    for i in range(size*size):
        if i != c and within_chebyshev(c, i, size, max_dist): moves.append(i)
    return moves

def play_match(board_init, p1_starts):
    board = board_init
    # P1 = Minimax, P2 = Pure MCTS
    p1 = MinimaxPlayer(depth=3)
    p2 = MCTSPure(n_playout=MCTS_PLAYOUTS)
    player_map = {1: p1 if p1_starts else p2, 2: p2 if p1_starts else p1}
    move_times = {1: [], 2: []}

    while True:
        end, winner = board.game_end()
        if end:
            # Return winner (1/2/-1) and avg times
            # winner is player ID (1 or 2). We need to know if it was Agent P1 or Agent P2.
            # If p1_starts is True: Agent P1 is Player 1.
            # If p1_starts is False: Agent P1 is Player 2.
            
            w_agent = None
            if winner != -1:
                if p1_starts: w_agent = "Minimax" if winner == 1 else "Pure"
                else: w_agent = "Minimax" if winner == 2 else "Pure"
            
            # Extract times
            t1 = np.mean(move_times[1])*1000 if move_times[1] else 0
            t2 = np.mean(move_times[2])*1000 if move_times[2] else 0
            
            times_dict = {"Minimax": t1 if p1_starts else t2, "Pure": t2 if p1_starts else t1}
            return w_agent, times_dict

        curr = board.get_current_player()
        st = time.perf_counter()
        move = player_map[curr].get_action(board)
        move_times[curr].append(time.perf_counter() - st)
        board.do_move(move)

def run():
    center = center_index(SIZE)
    second_moves = all_valid_second_moves(SIZE, MAX_DIST)
    
    # Metrics
    # Case A: Minimax (P1) starts first
    case_a = {"Minimax": 0, "Pure": 0, "Draws": 0}
    # Case B: Pure (P2) starts first
    case_b = {"Minimax": 0, "Pure": 0, "Draws": 0}
    
    all_times = {"Minimax": [], "Pure": []}

    print(f"Starting: Minimax vs Pure MCTS ({len(second_moves)*2} games)")
    start_total = time.time()

    for second_idx in tqdm(second_moves):
        # Case A
        b = MCTSBoard(width=SIZE, height=SIZE, n_in_row=N_IN_ROW)
        b.init_board(start_player=0); b.do_move(center); b.do_move(second_idx)
        w, t = play_match(b, p1_starts=True)
        all_times["Minimax"].append(t["Minimax"]); all_times["Pure"].append(t["Pure"])
        if w == "Minimax": case_a["Minimax"] += 1
        elif w == "Pure": case_a["Pure"] += 1
        else: case_a["Draws"] += 1

        # Case B
        b = MCTSBoard(width=SIZE, height=SIZE, n_in_row=N_IN_ROW)
        b.init_board(start_player=0); b.do_move(center); b.do_move(second_idx)
        w, t = play_match(b, p1_starts=False)
        all_times["Minimax"].append(t["Minimax"]); all_times["Pure"].append(t["Pure"])
        if w == "Minimax": case_b["Minimax"] += 1
        elif w == "Pure": case_b["Pure"] += 1
        else: case_b["Draws"] += 1

    total_time = time.time() - start_total
    tot = len(second_moves)

    print(f"\n=== TOTAL RUNTIME: {total_time:.2f} s ===")
    print(f"Average Minimax decision time: {np.mean(all_times['Minimax']):.2f} ms")
    print(f"Average Pure MCTS decision time: {np.mean(all_times['Pure']):.2f} ms\n")

    print(f"Case A: Minimax starts first (Minimax = player 1)")
    print(f"  Minimax wins: {case_a['Minimax']} / {tot} ({case_a['Minimax']/tot:.2%})")
    print(f"  Pure MCTS wins:    {case_a['Pure']} / {tot} ({case_a['Pure']/tot:.2%})")
    print(f"  Draws:        {case_a['Draws']} / {tot} ({case_a['Draws']/tot:.2%})\n")

    print(f"Case B: Pure MCTS starts first (Pure = player 1)")
    print(f"  Pure MCTS wins:    {case_b['Pure']} / {tot} ({case_b['Pure']/tot:.2%})")
    print(f"  Minimax wins: {case_b['Minimax']} / {tot} ({case_b['Minimax']/tot:.2%})")
    print(f"  Draws:        {case_b['Draws']} / {tot} ({case_b['Draws']/tot:.2%})\n")

if __name__ == "__main__": run()

"""
=== TOTAL RUNTIME: 103.55 s ===
Average Minimax decision time: 423.03 ms
Average Pure MCTS decision time: 693.71 ms

Case A: Minimax starts first (Minimax = player 1)
  Minimax wins: 8 / 8 (100.00%)
  Pure MCTS wins:    0 / 8 (0.00%)
  Draws:        0 / 8 (0.00%)

Case B: Pure MCTS starts first (Pure = player 1)
  Pure MCTS wins:    0 / 8 (0.00%)
  Minimax wins: 8 / 8 (100.00%)
  Draws:        0 / 8 (0.00%)
"""
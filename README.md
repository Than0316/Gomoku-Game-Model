# Gomoku AI Framework

## Introduction / Project Purpose
This project implements an artificial intelligence framework for **Gomoku** on reduced board sizes (**6×6** and **8×8**) with modified winning conditions: **four consecutive stones for 6×6** and **five consecutive stones for 8×8**.  
The reduced setting enables faster experimentation while preserving the essential strategic and adversarial properties of Gomoku.  

The framework includes classical **Minimax**, **heuristic evaluation**, **Monte Carlo Tree Search (MCTS)** variants, and **AlphaZero-style policy-value networks**, supporting both AI-vs-AI experiments and AI-vs-human play.

---

## Repository Structure

### 1. `EASY_GOMOKU`  
Implementation of Gomoku on a small board with baseline **Minimax** and evaluation functions. Includes scripts for training, evaluation, and gameplay.

- `EASY_GOMOKU_class_board.py` – Board representation and legal move generation.  
- `EASY_GOMOKU_class_shape.py` – Shape-based evaluation and pattern recognition.  
- `EASY_GOMOKU_evaluation_function.py` – Heuristic evaluation function for Minimax.  
- `EASY_GOMOKU_minimax.py` – Minimax implementation.  
- `EASY_GOMOKU_main.py` – Entry point for playing or running experiments.  
- `Makefile`, `make.bat` – Build and documentation scripts.

---

### 2. `SPEEDUP_EASY_GOMOKU`  
Optimized version of `EASY_GOMOKU` with performance improvements on evaluation and move generation.

---

### 3. `Gomoku_8_8`  
Gomoku on an 8×8 board with advanced agents:

- `GOMOKU_8x8_minimax.py` – Minimax agent.  
- `GOMOKU_8x8_eval.py` – Evaluation function for heuristic agents.  
- `GOMOKU_8x8_main.py` – Main entry point.  
- `best_policy_8_8_5.model` – Pretrained policy network for AlphaZero-style MCTS.

---

### 4. `Monte_Carlo_guided_GOMOKU`  
Contains MCTS variants for 6×6 Gomoku:

- `mcts_pure.py` – Standard MCTS with random rollouts.  
- `mcts_guided.py` – MCTS guided by heuristic evaluation.  
- `mcts_alphaZero.py` – MCTS guided by a policy-value network.  
- `policy_value_net_numpy.py` – Numpy implementation of policy-value network.  
- Human play scripts (`*_human_play.py`) for interactive testing.  
- `best_policy_6_6_4.model` – Pretrained policy network.

---

### 5. `mcts`  
General-purpose MCTS implementation with variants:

- `mcts_pure.py` – Vanilla MCTS.  
- `mcts_heuristic.py` – Heuristic-guided MCTS.  
- `mcts_alphaZero.py` – Policy-value guided MCTS.  
- `policy_value_net_numpy.py` – Numpy policy-value network backend.  
- `game.py`, `human_play.py` – Game loop and interactive play.

---

### 6. `comparisons`  
Scripts to compare different AI agents under controlled experiments:

- Scripts for 6×6 and 8×8 boards.  
- Matchups include: Minimax vs MCTS variants, MCTS pure vs guided, and AlphaZero vs heuristic.  
- Results can be used to analyze agent performance under different strategies and board sizes.

---

## Installation / Requirements
- Python 3.10+  
- NumPy
# Gomoku-Game-Model

This project implements an artificial intelligence framework for **Gomoku** on a reduced board size (**6×6**) with a modified winning condition of **four consecutive stones**.  
The reduced setting enables faster experimentation while preserving the essential strategic properties of adversarial board games.

---

## Project Overview

The project is structured in **two main stages**.

### Stage 1: Minimax-Based AI

The first stage focuses on implementing a **Minimax-based Gomoku AI**.  
This stage establishes a clear and explicit game model, including:

- board representation,
- move generation,
- terminal-state detection,
- heuristic evaluation function.

Beyond producing a playable AI, this stage serves to validate the correctness of the game mechanics and to identify the core components required for adversarial search.

### Stage 2: Monte Carlo Tree Search (MCTS)

Building on the Minimax foundation, the second stage—**the main objective of the project**—is the implementation of a **Monte Carlo Tree Search (MCTS)** algorithm.

The prior Minimax implementation facilitates this transition by providing:

- a well-defined game state representation,
- reusable game logic (legal moves, terminal checks),
- heuristic knowledge that can be adapted for rollout policies or node evaluation within MCTS.

---

## Repository Structure

- `EASY_GOMOKU/`  
  Main source directory containing the Gomoku game model and AI implementations.

  - `EASY_GOMOKU_main.py`  
    Entry point of the program. Handles game initialization and launches the interactive Gomoku game in the terminal.

  - `EASY_GOMOKU_minimax.py`  
    Implements the Minimax algorithm for adversarial search, including move selection for the AI player.

  - `EASY_GOMOKU_class_board.py`  
    Defines the board representation, game state, and core game mechanics such as legal move generation and terminal-state detection.

  - `EASY_GOMOKU_class_shape.py`  
    Encodes pattern (shape) detection logic used to identify strategic configurations on the board.

  - `EASY_GOMOKU_evaluation_function.py`  
    Implements the heuristic evaluation function based on detected board patterns, used by the Minimax algorithm to score game states.

- Other files and directories  
  Dedicated to documentation (Sphinx), experiments, or auxiliary materials.

---

## Documentation

The codebase is fully documented using Sphinx. The generated HTML documentation can be found in `build/html/index.html`.

---

## How to Run

The game can be played directly in the terminal.

1. Ensure you have a compatible Python environment.
2. Navigate to the project root directory.
3. Run the main file inside `EASY_GOMOKU`.

The program launches an interactive Gomoku game, where a human player competes against the AI.

---

## Current Status

- **Minimax-based AI**: implemented and functional.
- **MCTS**: under development.
- Board size and winning condition are intentionally simplified for clarity and computational efficiency.

---

## References

- Russell, S., & Norvig, P. *Artificial Intelligence: A Modern Approach*. Pearson.
- Browne, C. B., et al. *A Survey of Monte Carlo Tree Search Methods*. IEEE TCIAIG, 2012.

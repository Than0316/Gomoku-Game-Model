# -*- coding: utf-8 -*-
"""
A pure implementation of the Monte Carlo Tree Search (MCTS)

@author: Junxiao Song

Modifications:
- Guided rollout policy that prefers moves adjacent to existing stones
  and scores moves with a simple heuristic (immediate win > block opponent
  immediate win > extend own lines).
- Softmax sampling across candidate moves to keep rollouts stochastic.
- If the AI is to play first (board empty), choose (3,3) as the opening move
  when available.
"""
import math
import numpy as np
import copy
from operator import itemgetter


def _neighbors_of_existing_stones(board):
    """Return a list of available moves that are adjacent (8-neighborhood)
    to any existing stone on the board."""
    if not getattr(board, "states", None) or getattr(board, "width", None) is None:
        return list(board.availables)
    width = board.width
    height = getattr(board, "height", width)
    neighbor_positions = set()
    for pos in board.states.keys():
        row, col = divmod(pos, width)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = row + dx, col + dy
                if 0 <= nx < height and 0 <= ny < width:
                    neighbor_positions.add(nx * width + ny)
    candidates = [m for m in board.availables if m in neighbor_positions]
    if not candidates:
        # fallback to all availables if no neighbors (e.g. very first move)
        candidates = list(board.availables)
    return candidates


def _count_in_direction(states, width, move, player, dx, dy):
    """Count consecutive stones of `player` in both directions from `move`
    along (dx, dy). Does not include `move` itself."""
    h = move // width
    w = move % width
    count = 0
    # forward
    x, y = h + dx, w + dy
    while 0 <= x < width and 0 <= y < width and (x * width + y) in states and states[x * width + y] == player:
        count += 1
        x += dx
        y += dy
    # backward
    x, y = h - dx, w - dy
    while 0 <= x < width and 0 <= y < width and (x * width + y) in states and states[x * width + y] == player:
        count += 1
        x -= dx
        y -= dy
    return count


def _score_move_simple(board, move, player):
    """A small heuristic to score a candidate move for `player`.

    Scoring rules (simple and fast):
    - If placing here gives immediate win (line >= n_in_row): very large score.
    - If placing here blocks opponent's immediate win: high score.
    - Otherwise reward extending own contiguous lines (exponential in length).
    """
    if not getattr(board, "states", None) or getattr(board, "width", None) is None:
        return 0.0
    width = board.width
    n = board.n_in_row
    states = board.states
    opp = board.players[0] if player == board.players[1] else board.players[1]
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

    # Check immediate win for player
    for dx, dy in directions:
        own_len = _count_in_direction(states, width, move, player, dx, dy)
        if own_len + 1 >= n:
            return 1e6  # immediate win is best

    # Check immediate win for opponent (block)
    for dx, dy in directions:
        opp_len = _count_in_direction(states, width, move, opp, dx, dy)
        if opp_len + 1 >= n:
            return 5e5  # blocking opponent immediate win is second best

    # Otherwise, reward extending own lines and blocking partially opponent lines.
    score = 0.0
    for dx, dy in directions:
        own_len = _count_in_direction(states, width, move, player, dx, dy)
        opp_len = _count_in_direction(states, width, move, opp, dx, dy)
        # exponential weighting for longer runs (prefer extending longer runs)
        score += math.exp(own_len)
        # small bonus for reducing opponent's run potential
        score += 0.5 * math.exp(opp_len * 0.5)
    return score


def rollout_policy_fn(board, temperature=0.7):
    """Guided rollout policy:
    - prefer available moves adjacent to existing stones
    - score moves with a simple heuristic favoring immediate wins, blocks,
      and extensions of existing lines
    - use softmax sampling (temperature) to keep rollouts stochastic
    Returns an iterable of (move, prob) pairs (compatible with original code).
    """
    try:
        candidates = _neighbors_of_existing_stones(board)
        player = getattr(board, "current_player", None)
        # If board exposes current_player, score from that player's perspective;
        # otherwise, score using first player as a fallback (still useful heuristics).
        if player is None:
            player = board.players[0] if len(board.players) > 0 else 1

        scores = np.array([_score_move_simple(board, m, player) for m in candidates], dtype=float)
        # Numerical stability: shift scores
        if np.all(scores == 0):
            # fallback to uniform random among candidates
            probs = np.ones(len(candidates)) / len(candidates)
        else:
            # softmax with temperature
            scaled = scores / max(1e-9, temperature)
            # clip to avoid overflow
            scaled = np.clip(scaled, -700, 700)
            exps = np.exp(scaled - np.max(scaled))
            probs = exps / np.sum(exps)
    except Exception:
        # On any unexpected error, fallback to original uniform random over availables
        candidates = list(board.availables)
        probs = np.ones(len(candidates)) / len(candidates)

    return zip(candidates, probs)


def policy_value_fn(board):
    """a function that takes in a state and outputs a list of (action, probability)
    tuples and a score for the state"""
    # return uniform probabilities and 0 score for pure MCTS
    action_probs = np.ones(len(board.availables))/len(board.availables)
    return zip(board.availables, action_probs), 0


class TreeNode(object):
    """A node in the MCTS tree. Each node keeps track of its own value Q,
    prior probability P, and its visit-count-adjusted prior score u.
    """

    def __init__(self, parent, prior_p):
        self._parent = parent
        self._children = {}  # a map from action to TreeNode
        self._n_visits = 0
        self._Q = 0
        self._u = 0
        self._P = prior_p

    def expand(self, action_priors):
        """Expand tree by creating new children.
        action_priors: a list of tuples of actions and their prior probability
            according to the policy function.
        """
        for action, prob in action_priors:
            if action not in self._children:
                self._children[action] = TreeNode(self, prob)

    def select(self, c_puct):
        """Select action among children that gives maximum action value Q
        plus bonus u(P).
        Return: A tuple of (action, next_node)
        """
        return max(self._children.items(),
                   key=lambda act_node: act_node[1].get_value(c_puct))

    def update(self, leaf_value):
        """Update node values from leaf evaluation.
        leaf_value: the value of subtree evaluation from the current player's
            perspective.
        """
        # Count visit.
        self._n_visits += 1
        # Update Q, a running average of values for all visits.
        self._Q += 1.0*(leaf_value - self._Q) / self._n_visits

    def update_recursive(self, leaf_value):
        """Like a call to update(), but applied recursively for all ancestors.
        """
        # If it is not root, this node's parent should be updated first.
        if self._parent:
            self._parent.update_recursive(-leaf_value)
        self.update(leaf_value)

    def get_value(self, c_puct):
        """Calculate and return the value for this node.
        It is a combination of leaf evaluations Q, and this node's prior
        adjusted for its visit count, u.
        c_puct: a number in (0, inf) controlling the relative impact of
            value Q, and prior probability P, on this node's score.
        """
        self._u = (c_puct * self._P *
                   np.sqrt(self._parent._n_visits) / (1 + self._n_visits))
        return self._Q + self._u

    def is_leaf(self):
        """Check if leaf node (i.e. no nodes below this have been expanded).
        """
        return self._children == {}

    def is_root(self):
        return self._parent is None


class MCTS(object):
    """A simple implementation of Monte Carlo Tree Search."""

    def __init__(self, policy_value_fn, c_puct=5, n_playout=10000):
        """
        policy_value_fn: a function that takes in a board state and outputs
            a list of (action, probability) tuples and also a score in [-1, 1]
            (i.e. the expected value of the end game score from the current
            player's perspective) for the current player.
        c_puct: a number in (0, inf) that controls how quickly exploration
            converges to the maximum-value policy. A higher value means
            relying on the prior more.
        """
        self._root = TreeNode(None, 1.0)
        self._policy = policy_value_fn
        self._c_puct = c_puct
        self._n_playout = n_playout

    def _playout(self, state):
        """Run a single playout from the root to the leaf, getting a value at
        the leaf and propagating it back through its parents.
        State is modified in-place, so a copy must be provided.
        """
        node = self._root
        while(1):
            if node.is_leaf():

                break
            # Greedily select next move.
            action, node = node.select(self._c_puct)
            state.do_move(action)

        action_probs, _ = self._policy(state)
        # Check for end of game
        end, winner = state.game_end()
        if not end:
            node.expand(action_probs)
        # Evaluate the leaf node by random rollout
        leaf_value = self._evaluate_rollout(state)
        # Update value and visit count of nodes in this traversal.
        node.update_recursive(-leaf_value)

    def _evaluate_rollout(self, state, limit=1000, temperature=0.7):
        """Use the rollout policy to play until the end of the game,
        returning +1 if the current player wins, -1 if the opponent wins,
        and 0 if it is a tie.

        Sampling from rollout_policy_fn is now stochastic: we sample a move
        according to the probability distribution returned by rollout_policy_fn
        using np.random.choice. The temperature parameter (default 0.7) is
        passed down to the rollout_policy_fn to control randomness.
        """
        player = state.get_current_player()
        for i in range(limit):
            end, winner = state.game_end()
            if end:
                break
            # Obtain (move, prob) pairs from rollout policy
            try:
                action_probs_iter = rollout_policy_fn(state, temperature)
                action_probs = list(action_probs_iter)
                # Handle empty candidate list
                if not action_probs:
                    # fallback to uniform random from availables
                    avail = list(state.availables)
                    if not avail:
                        break
                    action = np.random.choice(avail)
                    state.do_move(action)
                    continue

                moves, probs = zip(*action_probs)
                probs = np.array(probs, dtype=float)

                # Validate probabilities: finite and positive sum
                if not np.isfinite(probs).all() or probs.sum() <= 0:
                    # fallback to uniform over moves
                    probs = np.ones(len(moves), dtype=float)

                # Normalize probabilities to sum to 1
                probs = probs / probs.sum()

                # If there's only one move, pick it deterministically
                if len(moves) == 1:
                    action = moves[0]
                else:
                    # Sample an index according to probs
                    idx = np.random.choice(len(moves), p=probs)
                    action = moves[int(idx)]

            except Exception:
                # Any unexpected error: fallback to uniform random move
                avail = list(state.availables)
                if not avail:
                    break
                action = np.random.choice(avail)

            state.do_move(action)
        else:
            # If no break from the loop, issue a warning.
            print("WARNING: rollout reached move limit")
        if winner == -1:  # tie
            return 0
        else:
            return 1 if winner == player else -1

    def get_move(self, state):
        """Runs all playouts sequentially and returns the most visited action.
        state: the current game state

        Return: the selected action
        """
        for n in range(self._n_playout):
            state_copy = copy.deepcopy(state)
            self._playout(state_copy)
        return max(self._root._children.items(),
                   key=lambda act_node: act_node[1]._n_visits)[0]

    def update_with_move(self, last_move):
        """Step forward in the tree, keeping everything we already know
        about the subtree.
        """
        if last_move in self._root._children:
            self._root = self._root._children[last_move]
            self._root._parent = None
        else:
            self._root = TreeNode(None, 1.0)

    def __str__(self):
        return "MCTS"


class MCTSPlayer(object):
    """AI player based on MCTS"""
    def __init__(self, c_puct=5, n_playout=2000):
        self.mcts = MCTS(policy_value_fn, c_puct, n_playout)

    def set_player_ind(self, p):
        self.player = p

    def reset_player(self):
        self.mcts.update_with_move(-1)

    def get_action(self, board):
        sensible_moves = board.availables
        if len(sensible_moves) > 0:
            # If board is empty and (3,3) is available, play it as the opening move.
            # This satisfies the "computer starts with 3,3" preference.
            if board.last_move == -1:
                center3 = board.location_to_move([3, 3])
                if center3 in sensible_moves:
                    # update tree with -1 to reset root as original code expected
                    self.mcts.update_with_move(-1)
                    return center3

            move = self.mcts.get_move(board)
            self.mcts.update_with_move(-1)
            return move
        else:
            print("WARNING: the board is full")

    def __str__(self):
        return "MCTS {}".format(self.player)
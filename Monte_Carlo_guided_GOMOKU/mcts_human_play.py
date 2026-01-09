# -*- coding: utf-8 -*-
"""
human VS AI models
Input your move in the format: 2,3

Modified so the AI uses the heuristic MCTS (mcts_pure) only.

@author: Junxiao Song
(modified by Than0316)
"""

from __future__ import print_function
import pickle
from mcts_game import Board, Game
from mcts_guided import MCTSPlayer as MCTS_Pure
# Note: we intentionally do not import the neural-network-based MCTS player here
# from mcts_alphaZero import MCTSPlayer
# and we don't need PolicyValueNetNumpy when using the heuristic pure MCTS
# from policy_value_net_numpy import PolicyValueNetNumpy


class Human(object):
    """
    human player
    """

    def __init__(self):
        self.player = None

    def set_player_ind(self, p):
        self.player = p

    def get_action(self, board):
        try:
            location = input("Your move: ")
            if isinstance(location, str):  # for python3
                location = [int(n, 10) for n in location.split(",")]
            move = board.location_to_move(location)
        except Exception as e:
            move = -1
        if move == -1 or move not in board.availables:
            print("invalid move")
            move = self.get_action(board)
        return move

    def __str__(self):
        return "Human {}".format(self.player)


def run():
    n = 4
    width, height = 6, 6

    try:
        board = Board(width=width, height=height, n_in_row=n)
        game = Game(board)

        # ############### human VS AI ###################
        # Use the heuristic pure MCTS player (the version in mcts_pure.py
        # which includes your pattern-based rollout heuristic).
        mcts_player = MCTS_Pure(c_puct=5, n_playout=400)  # set larger n_playout for better play

        # human player, input your move in the format: 2,3
        human = Human()

        # set start_player=0 for human first, start_player=1 for AI first
        game.start_play(human, mcts_player, start_player=1, is_shown=1)
    except KeyboardInterrupt:
        print('\n\rquit')


if __name__ == '__main__':
    run()
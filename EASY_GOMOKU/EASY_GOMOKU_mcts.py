import math
import random
import time

class MCTSNode:
    def __init__(self, board, parent=None, move=None):
        self.board = board
        self.parent = parent
        self.move = move
        self.children = []
        self.untried_moves = board.legal_moves()
        self.wins = 0
        self.visits = 0
        self.player_just_moved = 'O' if board.player == 'X' else 'X'

    def uct_select_child(self):
        """
        Upper Confidence Bound 1 applied to trees.
        Balances exploring new moves vs sticking to winning moves.
        """
        # C is the exploration parameter. sqrt(2) is standard.
        # Higher C = explore more. Lower C = exploit known wins more.
        C = 1.414 
        s = sorted(self.children, key=lambda c: c.wins/c.visits + C * math.sqrt(math.log(self.visits)/c.visits))
        return s[-1]

    def add_child(self, move, state):
        """
        Creates a new child node.
        """
        node = MCTSNode(state, parent=self, move=move)
        self.untried_moves.remove(move)
        self.children.append(node)
        return node

    def update(self, result):
        """
        Updates the node stats with the result of a simulation.
        Result is 1 if this node's player won, 0 for draw, -1 for loss.
        """
        self.visits += 1
        self.wins += result

def mcts_search(root_board, time_limit=3.0):
    """
    The main MCTS entry point.
    root_board: The current actual game board.
    time_limit: How many seconds to think.
    """
    root_node = MCTSNode(root_board)
    end_time = time.time() + time_limit
    
    # 1. Loop until time runs out
    count = 0
    while time.time() < end_time:
        node = root_node
        state = root_board.copy() # Important: Work on a copy!

        # 2. SELECT
        # Dig down the tree to a node that isn't fully expanded
        while node.untried_moves == [] and node.children != []:
            node = node.uct_select_child()
            state = state.play(node.move)

        # 3. EXPAND
        # If there are moves we haven't tried at this node, try one
        if node.untried_moves != []:
            m = random.choice(node.untried_moves)
            state = state.play(m)
            node = node.add_child(m, state)

        # 4. SIMULATE (Rollout)
        # Play randomly until game over
        while not state.is_full():
            # Optimization: Check if the previous move just won the game
            # 'state.player' is the next person to move. 
            # So we check if the person who JUST moved won.
            prev_player = 'O' if state.player == 'X' else 'X'
            if state.check_winner(prev_player):
                break
            
            moves = state.legal_moves()
            if not moves: break
            
            # Pure MCTS picks fully random. 
            # Note: This is where "Pure" MCTS is weak in Gomoku.
            m = random.choice(moves)
            state = state.play(m)

        # 5. BACKPROPAGATE
        # Who won the simulation?
        # We need to score from the perspective of the player at the Node.
        winner = None
        if state.check_winner('X'): winner = 'X'
        elif state.check_winner('O'): winner = 'O'
        
        while node != None:
            if winner is None:
                # Draw
                node.update(0.5)
            elif winner == node.player_just_moved:
                # This node represents a move by 'player_just_moved'.
                # If that player won the simulation, this was a good move.
                node.update(1.0)
            else:
                # The other player won
                node.update(0.0)
            node = node.parent
        
        count += 1

    print(f"MCTS Simulations: {count}")
    
    # Return the move with the most visits (most robust choice)
    if not root_node.children:
        return None
        
    return sorted(root_node.children, key=lambda c: c.visits)[-1].move
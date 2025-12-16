# Gomoku-Game-Model
Prunning VS MCTS

git add .
git commit -m "Describe your changes"
git push

We can improve efficiency by only counting the score at each state to avoid scanning the board multiple times. 

For example, win if the score of a player bigger then 1000000. 

While doing alpha-beta, we prioritise cases where score > 100000 because it's a double threat that leads to an immediate win.

For each move, we compute only the additional score it created and we just add it to the total score. To do that, we can set the shape detector such that it takes the new move and check two positions next to that move the new shape it created. We call then the evaluation function to turn these shapes into scores.

The move generator prioritise positions related to threats and that way we can increase the efficiency of our program.

We can use Monte Carlo or other learning techniques to order general cases where threats are not possible.

###___### my comments

We need to be more detailed on shape detector and evaluation function.
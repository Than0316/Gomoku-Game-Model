from EASY_GOMOKU_class_board import Board
from EASY_GOMOKU_evaluation_function import evaluate, SCORES
from EASY_GOMOKU_class_shape import ShapeDetector
from EASY_GOMOKU_minimax import find_best_move

def debug_scenario():
    # 1. Reconstruct the board state where the AI failed
    # Rows 0-5. 
    # Row 3 (Index 2) has 'O' at Col 3 (Index 2)
    # Row 4 (Index 3) has 'XX' at Col 3,4 (Indices 2,3)
    
    grid = [
        ['-', '-', '-', '-', '-', '-'], # Row 0
        ['-', '-', '-', '-', '-', '-'], # Row 1
        ['-', '-', 'O', '-', '-', '-'], # Row 2 (AI)
        ['-', '-', 'X', 'X', '-', '-'], # Row 3 (Human Threat --XX--)
        ['-', '-', '-', '-', '-', '-'], # Row 4
        ['-', '-', '-', '-', '-', '-'], # Row 5
    ]
    
    board = Board(grid=grid, player='O') # It is AI's turn ('O')
    
    print("\n--- DEBUGGING BOARD STATE ---")
    board.print_board()

    # 2. Check Shape Detection
    print("\n--- STEP 1: SHAPE DETECTION ---")
    detector = ShapeDetector(board.grid)
    
    # Check what it sees for Human ('X')
    opp_counts = detector.count_patterns('X')
    print("Patterns detected for Opponent (X):")
    for shape, count in opp_counts.items():
        if count > 0:
            print(f"  {shape}: {count}")
            
    # Check if OPEN_2 is detected
    if opp_counts['OPEN_2'] > 0:
        print(">> SUCCESS: AI detected the OPEN_2 threat.")
    else:
        print(">> FAIL: AI did NOT detect the OPEN_2 threat.")

    # 3. Check Evaluation Score
    print("\n--- STEP 2: SCORING ---")
    score = evaluate(board, 'O')
    print(f"Current Board Score for AI (O): {score}")
    
    # Analyze the penalty
    # If detection worked, score should be very negative (e.g., -30,000)
    expected_penalty = -(SCORES['OPEN_2'] * 3) 
    if score < -10000:
        print(f">> SUCCESS: Score is heavily penalized (Expected ~{expected_penalty}).")
    else:
        print(f">> FAIL: Score is too high. The penalty logic isn't triggering.")

    # 4. Check Move Generation (Depth 1 vs Depth 3)
    print("\n--- STEP 3: SEARCH TEST ---")
    
    print("Running Search at Depth 1 (Immediate reaction)...")
    move1 = find_best_move(board, depth=1)
    print(f"Best Move (Depth 1): {move1}")
    
    print("\nRunning Search at Depth 3 (Lookahead)...")
    move3 = find_best_move(board, depth=4)
    print(f"Best Move (Depth 3): {move3}")
    
    # Check if it blocks
    # Blocking moves are (3, 1) or (3, 4) -> indices [3][1] or [3][4]
    blocking_moves = [(3, 1), (3, 4)]
    
    if move3 in blocking_moves:
        print("\n>> RESULT: AI CORRECTLY BLOCKS.")
    else:
        print(f"\n>> RESULT: AI FAILED. It played {move3} instead of blocking.")

if __name__ == "__main__":
    debug_scenario()
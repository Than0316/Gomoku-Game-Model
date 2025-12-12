import time
import sys
import re # Used for cleaning input
from GOMOKU_class_board import Board
from GOMOKU_evaluation_function import Evaluator, FIVE
from GOMOKU_alpha_beta import minmax, MAX_SCORE
from GOMOKU_config import Config


# --- Helper Functions ---

def initialize_board(size=Config.size):
    """Initializes the board and connects the evaluator."""
    b = Board(size)
    b.evaluator = Evaluator(size)
    return b

def parse_board_input_console(size):
    """
    Reads exactly 'size' valid rows from the console.
    This works perfectly with copy-pasting.
    """
    print(f"\n--- Enter {size}x{size} Board State ---")
    print("Use 'O' (Black), 'X' (White), '-' (Empty).")
    print(f"Paste your {size} lines below. The AI will start immediately after the last line.")
    
    input_board = []
    valid_rows_count = 0
    
    while valid_rows_count < size:
        try:
            # Read one line
            raw_line = input()
            
            # Clean the line: Remove spaces and keep only valid chars
            # We allow '0' as well just in case, treating it as empty like '-'
            clean_line = re.sub(r'[^O0X\-]', '', raw_line.upper())
            
            # Skip empty lines (often happen during pasting)
            if not clean_line:
                continue
                
            # Validation
            if len(clean_line) != size:
                print(f"Error: Row {valid_rows_count} has {len(clean_line)} valid characters. Expected {size}.")
                print(f"Content parsed: '{clean_line}'")
                print("Please enter this row again correctly:")
                continue
            
            # Convert to internal format
            row_data = []
            for char in clean_line:
                if char == 'O':
                    row_data.append(1)
                elif char == 'X':
                    row_data.append(-1)
                elif char == '-' or char == '0':
                    row_data.append(0)
            
            input_board.append(row_data)
            valid_rows_count += 1
            
            # Optional: Feedback so you know it's working
            # print(f"Row {valid_rows_count}/{size} accepted.")

        except EOFError:
            print("Input stream closed unexpectedly.")
            break
            
    return input_board

def sync_board_and_evaluator(board: Board, input_data: list):
    """
    Sets the main Board state and synchronizes the Evaluator's internal score tables.
    """
    black_count = 0
    white_count = 0
    
    # 1. Reset board
    board.board = [[0 for _ in range(board.size)] for _ in range(board.size)]
    board.history = []
    
    # 2. Determine player counts and set board
    for r in range(board.size):
        for c in range(board.size):
            role = input_data[r][c]
            if role != 0:
                board.board[r][c] = role
                if role == 1:
                    black_count += 1
                else:
                    white_count += 1
    
    # 3. Determine current player
    if black_count == white_count:
        current_role = 1 # Black's turn
    elif black_count > white_count:
        current_role = -1 # White's turn
    else:
        print("Warning: White has more stones than Black. Assuming Black's turn (1).")
        current_role = 1
        
    board.current_role = current_role
    
    # 4. Sync Evaluator
    board.evaluator.__init__(board.size) # Reset
    
    # Place existing stones on evaluator
    for r in range(board.size):
        for c in range(board.size):
            role = input_data[r][c]
            if role != 0:
                board.evaluator.board[r+1][c+1] = role 

    # Initialize scores for empty spots
    for r in range(board.size):
        for c in range(board.size):
            if board.board[r][c] == 0:
                 board.evaluator._update_single_point(r, c, 1)
                 board.evaluator._update_single_point(r, c, -1)
    
    return current_role

def get_best_move_iterative(board: Board, role: int, time_limit: float):
    """
    Iterative Deepening Search with hard time limit.
    """
    start_time = time.time()
    best_move_global = None
    best_score_global = -MAX_SCORE
    
    current_depth = 4 # Start a bit deeper to be useful
    max_depth = 12
    
    print(f"\n--- AI Thinking (Role {'O' if role == 1 else 'X'}) ---")
    
    while True:
        elapsed = time.time() - start_time
        if elapsed >= time_limit:
            break
        
        if current_depth > max_depth:
            break

        print(f"Searching depth {current_depth}...")
        
        # Heuristic: If we are deep (6+) and low on time, stop before starting a new depth
        if current_depth > 4 and (time_limit - elapsed) < 1.0:
             print("Insufficient time for next depth. Stopping.")
             break

        # Run Minimax
        # We catch potential errors here to ensure we return *something* even if a crash happens deeper
        try:
            score, move, path = minmax(board, role, depth=current_depth, enable_vct=True)
        except Exception as e:
            print(f"Search interrupted at depth {current_depth}: {e}")
            break
        
        # Record result if we finished this depth within time (mostly)
        if move:
            best_score_global = score
            best_move_global = move
            print(f"  > Depth {current_depth} completed: Move {move} (Score: {score})")

            if score >= FIVE:
                print("  > Forced WIN detected. Stopping early.")
                break
        
        current_depth += 2

    return best_move_global

def main():
    try:
        BOARD_SIZE = Config.size 
        TIME_LIMIT = 5.0 # Seconds
        
        game_board = initialize_board(BOARD_SIZE)

        print("\n=============================================")
        print("GOMOKU AI TERMINAL ANALYZER")
        print(f"Board Size: {BOARD_SIZE}x{BOARD_SIZE} | Search Time Limit: {TIME_LIMIT} seconds")
        print("=============================================")

        # 1. Read input board
        input_data = parse_board_input_console(BOARD_SIZE)
        
        # 2. Sync state and determine role
        ai_role = sync_board_and_evaluator(game_board, input_data)
        
        # 3. Find best move
        start_search = time.time()
        best_move = get_best_move_iterative(game_board, ai_role, TIME_LIMIT)
        end_search = time.time()

        # 4. Output Result
        print("\n=============================================")
        print("AI ANALYSIS COMPLETE")
        print(f"Total Search Time: {end_search - start_search:.2f} seconds")
        print(f"AI Turn: {'Black (O)' if ai_role == 1 else 'White (X)'}")
        
        if best_move:
            r, c = best_move
            print(f"BEST MOVE: ({r}, {c})")
            
            # Convert to Algebra (A1, B5, etc)
            col_letter = chr(ord('A') + c)
            # Gomoku convention often puts A at bottom or top, here we assume standard Matrix: row 0 is top
            # Usually row index 0 -> 15 (or 1), col index 0 -> A
            print(f"Algebraic: {col_letter}{r + 1}") # 1-based index for rows
            
            # Display board with the move played
            game_board.put(r, c, ai_role)
            game_board.evaluator.move(r, c, ai_role)
            print("\nBoard state after AI move:")
            game_board.display()
            
        else:
            print(f"AI could not find a move within {TIME_LIMIT} seconds.")
        print("=============================================")

    except ValueError as e:
        print(f"\nFATAL ERROR: {e}")
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
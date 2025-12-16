from enum import IntEnum

class ShapeType(IntEnum):
    """
    Enum representing the different shapes and their heuristic scores.
    These values match the logic in the JS 'shapes' constant.
    ###___### We can create a method that detects all the shapes that each new stone creates to avoid scanning the board multiple times
    """
    ###___### this part is in evaluation function, shape type only look for shape
    FIVE = 5
    BLOCK_FIVE = 50  # Win but blocked on one side (still a win)
    FOUR = 4         # Open four (guaranteed win next turn)
    FOUR_FOUR = 44   # Double four
    FOUR_THREE = 43  # Four and Three
    THREE_THREE = 33 # Double three
    BLOCK_FOUR = 40  # Closed four (needs another move to become 5)
    THREE = 3        # Open three
    BLOCK_THREE = 30 # Closed three
    TWO_TWO = 22     # Double two
    TWO = 2          # Open two
    NONE = 0

class ShapeDetector:
    """
    Contains logic to detect shapes on the board.
    Translates the 'getShapeFast' logic from the reference implementation.
    """

    @staticmethod
    def get_shape(board_grid, x, y, offset_x, offset_y, role):
        """
        Analyzes the shape formed at (x, y) in the direction (offset_x, offset_y).
        
        Args:
            board_grid: 2D array of the board.
            x, y: Coordinates of the stone being analyzed.
            offset_x, offset_y: Direction vector (e.g., (1, 0) for horizontal).
            role: 1 (Black) or -1 (White).
            
        Returns:
            (ShapeType, self_count)
        """
        size = len(board_grid)
        
        # Optimization: Check 2 steps out in both directions. 
        # If both are strictly empty/out-of-bounds in a way that prevents 5, skip.
        # (Simplified bounds check for Python safety)
        if not (0 <= x + offset_x < size and 0 <= y + offset_y < size):
            return ShapeType.NONE, 1
            
        # Scan 'left' (negative direction) and 'right' (positive direction)
        left = ShapeDetector._count_shape(board_grid, x, y, -offset_x, -offset_y, role)
        right = ShapeDetector._count_shape(board_grid, x, y, offset_x, offset_y, role)

        self_count = left['self_count'] + right['self_count'] + 1
        total_length = left['total_length'] + right['total_length'] + 1
        no_empty_self_count = left['no_empty_self_count'] + right['no_empty_self_count'] + 1
        
        # Calculates "One Jump" count (e.g., XX X)
        one_empty_self_count = max(
            left['one_empty_self_count'] + right['no_empty_self_count'],
            left['no_empty_self_count'] + right['one_empty_self_count']
        ) + 1

        left_empty = left['side_empty_count']
        right_empty = right['side_empty_count']

        if total_length < 5:
            return ShapeType.NONE, self_count

        # --- Shape Classification Logic ---
        
        # Five in a row
        if no_empty_self_count >= 5:
            if left_empty > 0 and right_empty > 0:
                return ShapeType.FIVE, self_count
            else:
                return ShapeType.BLOCK_FIVE, self_count
        
        # Four
        if no_empty_self_count == 4:
            # Check if it's an "Open Four" (Empty on both sides or special jump cases)
            if (left_empty > 0 and right_empty > 0) or \
               (left_empty > 0 and right['one_empty_self_count'] > right['no_empty_self_count']) or \
               (right_empty > 0 and left['one_empty_self_count'] > left['no_empty_self_count']):
                return ShapeType.FOUR, self_count
            else:
                return ShapeType.BLOCK_FOUR, self_count

        # Blocked Four created by a jump (e.g., X XXX)
        if one_empty_self_count == 4:
            return ShapeType.BLOCK_FOUR, self_count

        # Three
        if no_empty_self_count == 3:
            if (left_empty > 0 and right_empty > 0):
                # We typically need more space for a true Open Three
                if (left_empty >= 1 and right_empty >= 2) or (left_empty >= 2 and right_empty >= 1):
                     return ShapeType.THREE, self_count
                else:
                     return ShapeType.BLOCK_THREE, self_count
            else:
                return ShapeType.BLOCK_THREE, self_count
        
        # Three with a jump (e.g., X XX)
        if one_empty_self_count == 3:
            if left_empty > 0 and right_empty > 0:
                return ShapeType.THREE, self_count
            else:
                return ShapeType.BLOCK_THREE, self_count

        # Two (Open Two)
        if no_empty_self_count == 2:
            if left_empty > 0 and right_empty > 0 and total_length > 5: # Need space to grow
                return ShapeType.TWO, self_count

        return ShapeType.NONE, self_count

    @staticmethod
    def _count_shape(board, x, y, dx, dy, role):
        """
        Helper function to scan in one specific direction.
        Returns detailed stats about stones and gaps found.
        """
        size = len(board)
        opponent = -role
        
        inner_empty_count = 0
        temp_empty_count = 0
        self_count = 0
        total_length = 0
        
        side_empty_count = 0
        no_empty_self_count = 0
        one_empty_self_count = 0
        
        # Scan up to 5 steps away
        for i in range(1, 6):
            nx, ny = x + i * dx, y + i * dy
            
            # Check bounds
            if not (0 <= nx < size and 0 <= ny < size):
                break
                
            current_role = board[nx][ny]
            
            # If we hit an opponent or out of bounds (handled by loop end), stop
            if current_role == opponent:
                break
            
            if current_role == role:
                self_count += 1
                side_empty_count = 0 # Reset side empty because we found a stone
                
                # If we had a gap previously, add it to inner gaps
                if temp_empty_count > 0:
                    inner_empty_count += temp_empty_count
                    temp_empty_count = 0
                
                # Update continuous counts
                if inner_empty_count == 0:
                    no_empty_self_count += 1
                    one_empty_self_count += 1
                elif inner_empty_count == 1:
                    one_empty_self_count += 1
            
            total_length += 1
            
            if current_role == 0:
                temp_empty_count += 1
                side_empty_count += 1
                # If we hit 2 empty spaces in a row, usually shape ends there
                if side_empty_count >= 2:
                    break
        
        # Reset one_empty count if no inner gap was actually found
        if inner_empty_count == 0:
            one_empty_self_count = 0
            
        return {
            'self_count': self_count,
            'total_length': total_length,
            'no_empty_self_count': no_empty_self_count,
            'one_empty_self_count': one_empty_self_count,
            'inner_empty_count': inner_empty_count,
            'side_empty_count': side_empty_count
        }
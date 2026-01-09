from GOMOKU_8x8_config import Config

class ShapeDetector:
    def __init__(self, grid):
        self.lines = self._get_all_lines(grid)

    def _get_all_lines(self, grid):
        lines = []
        # Rows & Cols
        for r in range(Config.SIZE): lines.append("".join(grid[r]))
        for c in range(Config.SIZE): lines.append("".join(grid[r][c] for r in range(Config.SIZE)))
        
        # Diagonals (Length must be >= 5)
        # Top-Left to Bottom-Right
        for k in range(-(Config.SIZE - 5), Config.SIZE - 5 + 1):
            lines.append("".join(grid[r][r+k] for r in range(Config.SIZE) if 0 <= r+k < Config.SIZE))
        # Top-Right to Bottom-Left
        for k in range(4, 2 * Config.SIZE - 5):
            lines.append("".join(grid[r][k-r] for r in range(Config.SIZE) if 0 <= k-r < Config.SIZE))
        return lines

    def count_patterns(self, player):
        counts = {
            'WIN': 0, 'OPEN_4': 0, 'BLOCKED_4': 0, 
            'OPEN_3': 0, 'BLOCKED_3': 0, 'OPEN_2': 0, 'BLOCKED_2': 0
        }
        
        # P=Player, -=Empty. 
        # We replace found patterns to avoid double counting.
        
        for line in self.lines:
            # 1. WIN (XXXXX)
            if player * 5 in line: 
                counts['WIN'] += 1; continue

            # 2. OPEN 4 (-XXXX-) -> Guaranteed Win
            p_open4 = f"-{player*4}-"
            if p_open4 in line: 
                counts['OPEN_4'] += 1; line = line.replace(p_open4, "#####")

            # 3. BLOCKED 4 (OXXXX-, -XXXXO, XX-XX, XXX-X, X-XXX)
            # Simple connected blocked 4
            if f"-{player*4}" in line: counts['BLOCKED_4'] += 1; line = line.replace(f"-{player*4}", "####")
            if f"{player*4}-" in line: counts['BLOCKED_4'] += 1; line = line.replace(f"{player*4}-", "####")
            
            # Split 4s (Jump 4)
            split_4s = [f"{player*3}-{player}", f"{player}-{player*3}", f"{player*2}-{player*2}"]
            for p in split_4s:
                if p in line: counts['BLOCKED_4'] += 1; line = line.replace(p, "####")

            # 4. OPEN 3 (-XXX-)
            p_open3 = f"-{player*3}-"
            if p_open3 in line:
                counts['OPEN_3'] += 1; line = line.replace(p_open3, "####")

            # 5. OPEN 2 (-XX-)
            if f"-{player*2}-" in line:
                counts['OPEN_2'] += 1

        return counts
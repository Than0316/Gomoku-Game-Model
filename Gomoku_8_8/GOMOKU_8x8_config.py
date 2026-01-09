class Config:
    SIZE = 8
    WIN_LENGTH = 5
    EMPTY = '-'
    
    # Search Settings
    TIME_LIMIT = 4.8  # Seconds (leave slight buffer under 5s)
    MAX_DEPTH = 6     # Hard cap on depth
    
    # Scoring
    SCORES = {
        'WIN': 1_000_000_000,
        'OPEN_4': 10_000_000,    # -XXXX- (Unstoppable Win)
        'BLOCKED_4': 100_000,    # OXXXX- or XX-XX (Must Block)
        'OPEN_3': 10_000,        # -XXX- (Major Threat)
        'BLOCKED_3': 1_000,
        'OPEN_2': 100,
        'BLOCKED_2': 10
    }
from GOMOKU_config import Config

class Cache:
    """
    A simple FIFO (First-In, First-Out) cache implementation.
    Used as a Transposition Table to store and reuse results from previously
    searched board states (keyed by hash).
    """
    def __init__(self, capacity=1000000):
        self.capacity = capacity
        # Using a list for the FIFO queue and a dictionary for quick lookup
        self.cache_queue = []
        self.map = {}
        self.hits = {'search': 0, 'total': 0, 'hit': 0}

    def get(self, key):
        """Retrieves a value based on the board hash."""
        self.hits['search'] += 1
        if not hasattr(Config, 'enable_cache') or not Config.enable_cache:
            return None
            
        if key in self.map:
            self.hits['hit'] += 1
            return self.map.get(key)
        return None

    def put(self, key, value):
        """Sets or inserts a value, managing the FIFO capacity."""
        if not hasattr(Config, 'enable_cache') or not Config.enable_cache:
            return
            
        if len(self.cache_queue) >= self.capacity:
            oldest_key = self.cache_queue.pop(0)
            if oldest_key in self.map:
                del self.map[oldest_key]
        
        if key not in self.map:
            self.cache_queue.append(key)
            self.hits['total'] += 1
        
        self.map[key] = value

    def has(self, key):
        """Checks if a key exists."""
        if not hasattr(Config, 'enable_cache') or not Config.enable_cache:
            return False
        return key in self.map
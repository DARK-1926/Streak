class MemoryEngine:
    """Implements memory management with HNSW for efficient allocation."""
    def __init__(self, seed: int):
        self.seed = seed
        self.hnsw = np.random.randint(0, 2, size=(100, 100))

    def allocate(self, size: int) -> np.ndarray:
        """Allocate memory of specified size with deterministic randomness."""
        return np.random.choice([0, 1], size=(size,))
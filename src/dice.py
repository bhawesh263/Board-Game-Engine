"""Dice class for the board game."""

import random
from typing import Optional


class Dice:
    """Represents a standard 6-sided dice."""
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the dice.
        
        Args:
            seed: Optional random seed for reproducible rolls (for testing)
        """
        self._random = random.Random(seed)
    
    def roll(self) -> int:
        """
        Roll the dice.
        
        Returns:
            A random number between 1 and 6
        """
        return self._random.randint(1, 6)
    
    def set_seed(self, seed: int):
        """Set the random seed for reproducible rolls."""
        self._random.seed(seed)

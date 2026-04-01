"""Player class for the board game."""


class Player:
    """Represents a player in the board game."""
    
    def __init__(self, player_id: int):
        """
        Initialize a player.
        
        Args:
            player_id: Unique identifier for the player (1-based)
        """
        self.id = player_id
        self.position = 0  # Start before field 1
        self.has_joker = False
        self.skip_next_turn = False
        self._activated_special_this_turn = False
    
    def move(self, steps: int) -> int:
        """
        Move the player by the given number of steps.
        
        Args:
            steps: Number of steps to move (can be negative)
            
        Returns:
            New position after movement
        """
        self.position += steps
        if self.position < 0:
            self.position = 0
        return self.position
    
    def give_joker(self) -> bool:
        """
        Give the player a joker if they don't have one.
        
        Returns:
            True if joker was given, False if player already has one
        """
        if not self.has_joker:
            self.has_joker = True
            return True
        return False
    
    def use_joker(self) -> bool:
        """
        Use the joker to avoid a trap.
        
        Returns:
            True if joker was used, False if player has no joker
        """
        if self.has_joker:
            self.has_joker = False
            return True
        return False
    
    def set_skip_turn(self):
        """Mark this player to skip their next turn."""
        self.skip_next_turn = True
    
    def should_skip_turn(self) -> bool:
        """
        Check if player should skip their turn and reset the flag.
        
        Returns:
            True if player should skip, False otherwise
        """
        if self.skip_next_turn:
            self.skip_next_turn = False
            return True
        return False
    
    def mark_special_activated(self):
        """Mark that player has activated a special field this turn."""
        self._activated_special_this_turn = True
    
    def can_activate_special(self) -> bool:
        """Check if player can activate a special field this turn."""
        return not self._activated_special_this_turn
    
    def reset_turn(self):
        """Reset turn-specific flags at the start of a new turn."""
        self._activated_special_this_turn = False
    
    def has_won(self) -> bool:
        """Check if player has passed field 30 and won."""
        return self.position > 30
    
    def __repr__(self) -> str:
        return f"Player({self.id}, pos={self.position}, joker={self.has_joker})"

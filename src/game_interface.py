"""Game Interface for simulation compatibility."""

from typing import Optional
from .game_engine import GameEngine  # type: ignore


class GameInterface:
    """
    Interface class for the board game simulation.
    
    This class provides the API expected by the simulation:
    - Initiation with number of players
    - Repeating calls to do turns with dice input
    """
    
    def __init__(self):
        """Initialize the interface (no game yet)."""
        self._engine: Optional[GameEngine] = None
    
    def init_game(self, num_players: int, seed: Optional[int] = None) -> dict:
        """
        Initialize a new game with the specified number of players.
        
        Args:
            num_players: Number of players (2-4)
            seed: Optional random seed for reproducible games
            
        Returns:
            Dict with initial game state
        """
        try:
            self._engine = GameEngine(num_players, seed=seed)
            return {
                "success": True,
                "message": f"Game initialized with {num_players} players",
                "state": self._engine.get_game_state()  # type: ignore
            }
        except ValueError as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def do_turn(self, dice_value: int) -> dict:
        """
        Execute a turn with the given dice value.
        
        The engine automatically determines which player's turn it is
        and tracks all game situations.
        
        Args:
            dice_value: The dice roll value (1-6)
            
        Returns:
            Dict with turn results
        """
        if self._engine is None:
            return {
                "success": False,
                "error": "Game not initialized. Call init_game first."
            }
        
        result = self._engine.do_turn(dice_value)  # type: ignore
        
        if "error" in result:
            return {
                "success": False,
                "error": result["error"]
            }
        
        return {
            "success": True,
            "turn_result": result,
            "state": self._engine.get_game_state()  # type: ignore
        }
    
    def get_state(self) -> dict:
        """
        Get the current game state.
        
        Returns:
            Dict with current game state
        """
        if self._engine is None:
            return {
                "success": False,
                "error": "Game not initialized"
            }
        
        return {
            "success": True,
            "state": self._engine.get_game_state()  # type: ignore
        }
    
    def get_current_player(self) -> dict:
        """
        Get information about whose turn it is.
        
        Returns:
            Dict with current player info
        """
        if self._engine is None:
            return {
                "success": False,
                "error": "Game not initialized"
            }
        
        if self._engine.game_over:  # type: ignore
            return {
                "success": True,
                "game_over": True,
                "winner": self._engine.winner.id  # type: ignore
            }
        
        player = self._engine.get_current_player()  # type: ignore
        return {
            "success": True,
            "game_over": False,
            "current_player": player.id,
            "position": player.position,
            "has_joker": player.has_joker
        }
    
    def is_game_over(self) -> bool:
        """Check if the game has ended."""
        return self._engine is not None and self._engine.game_over  # type: ignore
    
    def get_winner(self) -> Optional[int]:
        """Get the winner's player ID, or None if game not over."""
        if self._engine and self._engine.winner:  # type: ignore
            return self._engine.winner.id  # type: ignore
        return None
    
    def get_turn_log(self) -> list:
        """Get the complete log of all turns."""
        if self._engine is None:
            return []
        return self._engine.get_turn_log()  # type: ignore

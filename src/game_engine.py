"""Game Engine for the board game."""

from typing import List, Optional, Tuple, Dict, Any
from .player import Player  # type: ignore
from .board import Board, FieldType  # type: ignore
from .dice import Dice  # type: ignore


class GameEngine:
    """Main game engine that manages game state and rules."""
    
    MIN_PLAYERS = 2
    MAX_PLAYERS = 4
    
    def __init__(self, num_players: int, seed: Optional[int] = None):
        """
        Initialize a new game.
        
        Args:
            num_players: Number of players (2-4)
            seed: Optional random seed for reproducible games
            
        Raises:
            ValueError: If num_players is not between 2 and 4
        """
        if not self.MIN_PLAYERS <= num_players <= self.MAX_PLAYERS:
            raise ValueError(f"Number of players must be between {self.MIN_PLAYERS} and {self.MAX_PLAYERS}")
        
        self.board = Board(seed=seed)
        self.dice = Dice(seed=seed)
        self.players: List[Player] = [Player(i + 1) for i in range(num_players)]
        self.current_player_index = 0
        self.game_over = False
        self.winner: Optional[Player] = None
        self.turn_count = 0
        self._turn_log: List[dict] = []
    
    def get_current_player(self) -> Player:
        """Get the player whose turn it is."""
        return self.players[self.current_player_index]
    
    def _next_player(self):
        """Move to the next player, handling skip turns."""
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
    
    def do_turn(self, dice_value: Optional[int] = None) -> dict:
        """
        Execute a turn for the current player.
        
        Args:
            dice_value: Optional dice value (1-6). If None, dice is rolled.
            
        Returns:
            Dict containing turn results
        """
        if self.game_over:
            return {"error": "Game is already over", "winner": self.winner.id if self.winner else None}  # type: ignore
        
        player = self.get_current_player()
        player.reset_turn()
        
        # Check if player should skip turn
        if player.should_skip_turn():
            result = {
                "turn": self.turn_count,
                "player": player.id,
                "skipped": True,
                "reason": "skip_turn_effect"
            }
            self._turn_log.append(result)
            self._next_player()
            self.turn_count += 1
            return result
        
        # Roll dice or use provided value
        if dice_value is None:
            dice_value = self.dice.roll()
        elif not 1 <= dice_value <= 6:
            return {"error": f"Invalid dice value: {dice_value}. Must be 1-6."}
        
        # Move player
        old_position = player.position
        new_position = player.move(dice_value)
        
        result = {
            "turn": self.turn_count,
            "player": player.id,
            "dice": dice_value,
            "old_position": old_position,
            "new_position": new_position,
            "skipped": False,
            "field_activation": None,
            "game_over": False,
            "winner": None
        }
        
        # Check for win
        if player.has_won():
            self.game_over = True
            self.winner = player
            result["game_over"] = True
            result["winner"] = player.id
            self._turn_log.append(result)
            return result
        
        # Check for special field activation
        field = self.board.get_field(new_position)
        if field and field.field_type != FieldType.NORMAL:
            activation = field.activate(player, self.players)
            result["field_activation"] = activation
            
            # Check if player won after bonus movement
            if player.has_won():
                self.game_over = True
                self.winner = player
                result["game_over"] = True
                result["winner"] = player.id
        
        self._turn_log.append(result)
        self._next_player()
        self.turn_count += 1
        
        return result
    
    def get_game_state(self) -> dict:
        """
        Get the current state of the game.
        
        Returns:
            Dict with game state information
        """
        return {
            "turn_count": self.turn_count,
            "current_player": self.get_current_player().id if not self.game_over else None,
            "players": [
                {
                    "id": p.id,
                    "position": p.position,
                    "has_joker": p.has_joker,
                    "skip_next_turn": p.skip_next_turn
                }
                for p in self.players
            ],
            "special_fields": self.board.get_special_field_positions(),
            "game_over": self.game_over,
            "winner": self.winner.id if self.winner else None  # type: ignore
        }
    
    def get_turn_log(self) -> List[dict]:
        """Get the log of all turns played."""
        return self._turn_log.copy()
    
    def play_full_game(self, max_turns: int = 1000) -> dict:
        """
        Play a complete game automatically.
        
        Args:
            max_turns: Maximum number of turns before forcing game end
            
        Returns:
            Final game state
        """
        while not self.game_over and self.turn_count < max_turns:
            self.do_turn()
        
        return self.get_game_state()

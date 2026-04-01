"Board and Field classes for the board game."

import random
from enum import Enum
from typing import List, Optional, TYPE_CHECKING, Dict, Any

if TYPE_CHECKING:
    from .player import Player  # type: ignore


class FieldType(Enum):
    "Types of fields on the board."
    NORMAL = "normal"
    BONUS = "bonus"
    TRAP = "trap"


class BonusType(Enum):
    """Types of bonus effects."""
    MOVE_FORWARD_2 = 1  # Move forward 2 additional fields
    PUSH_OTHERS_BACK = 2  # All other players go back 2 fields
    JOKER = 3  # Save from next trap


class TrapType(Enum):
    """Types of trap effects."""
    MOVE_BACK_2 = 1  # Move back 2 fields
    PUSH_OTHERS_FORWARD = 2  # All other players move forward 2 fields
    SKIP_TURN = 3  # Skip next round


class Field:
    """Base class for a field on the board."""
    
    def __init__(self, position: int):
        self.position = position
        self.field_type = FieldType.NORMAL
    
    def activate(self, player: 'Player', all_players: List['Player']) -> dict:
        """
        Activate the field effect.
        
        Args:
            player: The player who landed on this field
            all_players: List of all players in the game
            
        Returns:
            Dict with activation result info
        """
        return {"activated": False, "type": "normal"}
    
    def __repr__(self) -> str:
        return f"Field({self.position})"


class BonusField(Field):
    """A bonus field that gives positive effects."""
    
    def __init__(self, position: int, seed: Optional[int] = None):
        super().__init__(position)
        self.field_type = FieldType.BONUS
        self._random = random.Random(seed)
    
    def activate(self, player: 'Player', all_players: List['Player']) -> dict:
        """Activate a random bonus effect."""
        if not player.can_activate_special():
            return {"activated": False, "reason": "already_activated_special"}
        
        bonus_type = BonusType(self._random.randint(1, 3))
        player.mark_special_activated()
        
        result: Dict[str, Any] = {
            "activated": True,
            "field_type": "bonus",
            "bonus_type": bonus_type.value,
            "effects": []
        }
        
        if bonus_type == BonusType.MOVE_FORWARD_2:
            player.move(2)
            result["effects"].append(f"Player {player.id} moved forward 2 fields to {player.position}")
            
        elif bonus_type == BonusType.PUSH_OTHERS_BACK:
            for other in all_players:
                if other.id != player.id:
                    other.move(-2)
                    result["effects"].append(f"Player {other.id} pushed back to {other.position}")
                    
        elif bonus_type == BonusType.JOKER:
            if player.give_joker():
                result["effects"].append(f"Player {player.id} received a joker")
            else:
                result["effects"].append(f"Player {player.id} already has a joker")
        
        return result
    
    def __repr__(self) -> str:
        return f"BonusField({self.position})"


class TrapField(Field):
    """A trap field that gives negative effects."""
    
    def __init__(self, position: int, seed: Optional[int] = None):
        super().__init__(position)
        self.field_type = FieldType.TRAP
        self._random = random.Random(seed)
    
    def activate(self, player: 'Player', all_players: List['Player']) -> dict:
        """Activate a random trap effect."""
        if not player.can_activate_special():
            return {"activated": False, "reason": "already_activated_special"}
        
        # Check for joker
        if player.use_joker():
            player.mark_special_activated()
            return {
                "activated": True,
                "field_type": "trap",
                "blocked_by_joker": True,
                "effects": [f"Player {player.id} used joker to avoid trap"]
            }
        
        trap_type = TrapType(self._random.randint(1, 3))
        player.mark_special_activated()
        
        result: Dict[str, Any] = {
            "activated": True,
            "field_type": "trap",
            "trap_type": trap_type.value,
            "blocked_by_joker": False,
            "effects": []
        }
        
        if trap_type == TrapType.MOVE_BACK_2:
            player.move(-2)
            result["effects"].append(f"Player {player.id} moved back 2 fields to {player.position}")
            
        elif trap_type == TrapType.PUSH_OTHERS_FORWARD:
            for other in all_players:
                if other.id != player.id:
                    other.move(2)
                    result["effects"].append(f"Player {other.id} pushed forward to {other.position}")
                    
        elif trap_type == TrapType.SKIP_TURN:
            player.set_skip_turn()
            result["effects"].append(f"Player {player.id} will skip next turn")
        
        return result
    
    def __repr__(self) -> str:
        return f"TrapField({self.position})"


class Board:
    """The game board with 30 fields."""
    
    TOTAL_FIELDS = 30
    NUM_BONUS_FIELDS = 5
    NUM_TRAP_FIELDS = 5
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the board with random special field placement.
        
        Args:
            seed: Optional random seed for reproducible field placement
        """
        self._random = random.Random(seed)
        self.fields: List[Field] = []
        self._setup_board()
    
    def _setup_board(self):
        """Create the board with randomly placed special fields."""
        # Start with all normal fields (positions 1-30)
        self.fields = [Field(i) for i in range(1, self.TOTAL_FIELDS + 1)]
        
        # Get available positions for special fields (indices 0-29)
        available_positions = list(range(self.TOTAL_FIELDS))
        self._random.shuffle(available_positions)
        
        # Place bonus fields
        bonus_positions = available_positions[:self.NUM_BONUS_FIELDS]  # type: ignore
        for pos in bonus_positions:
            self.fields[pos] = BonusField(pos + 1, seed=self._random.randint(0, 10000))
        
        # Place trap fields (no overlap guaranteed by slicing)
        trap_positions = available_positions[self.NUM_BONUS_FIELDS:self.NUM_BONUS_FIELDS + self.NUM_TRAP_FIELDS]  # type: ignore
        for pos in trap_positions:
            self.fields[pos] = TrapField(pos + 1, seed=self._random.randint(0, 10000))
    
    def get_field(self, position: int) -> Optional[Field]:
        """
        Get the field at a given position.
        
        Args:
            position: Field position (1-30)
            
        Returns:
            Field at that position, or None if position is out of bounds
        """
        if 1 <= position <= self.TOTAL_FIELDS:
            return self.fields[position - 1]
        return None
    
    def get_special_field_positions(self) -> dict:
        """
        Get positions of all special fields.
        
        Returns:
            Dict with 'bonus' and 'trap' lists of positions
        """
        bonus_positions = []
        trap_positions = []
        
        for field in self.fields:
            if field.field_type == FieldType.BONUS:
                bonus_positions.append(field.position)
            elif field.field_type == FieldType.TRAP:
                trap_positions.append(field.position)
        
        return {
            "bonus": sorted(bonus_positions),
            "trap": sorted(trap_positions)
        }
    
    def __repr__(self) -> str:
        special = self.get_special_field_positions()
        return f"Board(bonus={special['bonus']}, trap={special['trap']})"

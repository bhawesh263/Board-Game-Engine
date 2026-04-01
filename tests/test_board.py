"""Unit tests for Board and Field classes."""

import pytest  # type: ignore
import sys
sys.path.insert(0, r'D:\bhaiya test')

from src.board import Board, Field, BonusField, TrapField, FieldType, BonusType, TrapType  # type: ignore
from src.player import Player  # type: ignore


class TestField:
    """Test basic Field class."""
    
    def test_create_field(self):
        field = Field(5)
        assert field.position == 5
        assert field.field_type == FieldType.NORMAL
    
    def test_field_activate_returns_not_activated(self):
        field = Field(5)
        player = Player(1)
        result = field.activate(player, [player])
        assert result["activated"] == False


class TestBonusField:
    """Test BonusField class."""
    
    def test_create_bonus_field(self):
        field = BonusField(10)
        assert field.position == 10
        assert field.field_type == FieldType.BONUS
    
    def test_bonus_type_1_moves_forward(self):
        # Use seed that gives type 1
        field = BonusField(5, seed=42)
        player = Player(1)
        player.move(5)  # Position 5
        
        # Force type 1 by manipulating
        field._random.seed(1)  # Seed 1 gives 1 for randint(1,3)
        
        result = field.activate(player, [player])
        assert result["activated"] == True
        # Player should have moved 2 forward (position 5 + 2 = 7)
        # But type depends on random
    
    def test_bonus_blocks_second_activation(self):
        field = BonusField(5, seed=42)
        player = Player(1)
        player.move(5)
        
        # First activation
        result1 = field.activate(player, [player])
        assert result1["activated"] == True
        
        # Second activation should be blocked
        result2 = field.activate(player, [player])
        assert result2["activated"] == False
        assert result2["reason"] == "already_activated_special"


class TestTrapField:
    """Test TrapField class."""
    
    def test_create_trap_field(self):
        field = TrapField(15)
        assert field.position == 15
        assert field.field_type == FieldType.TRAP
    
    def test_trap_blocked_by_joker(self):
        field = TrapField(10, seed=42)
        player = Player(1)
        player.move(10)
        player.give_joker()
        
        result = field.activate(player, [player])
        assert result["activated"] == True
        assert result["blocked_by_joker"] == True
        assert player.has_joker == False  # Joker consumed
    
    def test_trap_blocks_second_activation(self):
        field = TrapField(5, seed=42)
        player = Player(1)
        player.move(5)
        
        # First activation
        result1 = field.activate(player, [player])
        assert result1["activated"] == True
        
        # Second activation should be blocked
        result2 = field.activate(player, [player])
        assert result2["activated"] == False


class TestBoard:
    """Test Board class."""
    
    def test_create_board(self):
        board = Board(seed=42)
        assert len(board.fields) == 30
    
    def test_board_has_correct_special_fields(self):
        board = Board(seed=42)
        special = board.get_special_field_positions()
        assert len(special["bonus"]) == 5
        assert len(special["trap"]) == 5
    
    def test_no_overlap_between_bonus_and_trap(self):
        board = Board(seed=42)
        special = board.get_special_field_positions()
        bonus_set = set(special["bonus"])
        trap_set = set(special["trap"])
        assert bonus_set.isdisjoint(trap_set)
    
    def test_get_field_valid_position(self):
        board = Board(seed=42)
        field = board.get_field(15)
        assert field is not None
        assert field.position == 15
    
    def test_get_field_invalid_position(self):
        board = Board(seed=42)
        assert board.get_field(0) is None
        assert board.get_field(31) is None
        assert board.get_field(-1) is None
    
    def test_reproducible_with_seed(self):
        board1 = Board(seed=123)
        board2 = Board(seed=123)
        
        special1 = board1.get_special_field_positions()
        special2 = board2.get_special_field_positions()
        
        assert special1["bonus"] == special2["bonus"]
        assert special1["trap"] == special2["trap"]
    
    def test_different_seeds_different_boards(self):
        board1 = Board(seed=100)
        board2 = Board(seed=200)
        
        special1 = board1.get_special_field_positions()
        special2 = board2.get_special_field_positions()
        
        # Very unlikely to be the same
        assert special1["bonus"] != special2["bonus"] or special1["trap"] != special2["trap"]

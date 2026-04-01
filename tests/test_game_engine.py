"""Unit tests for GameEngine class."""

import pytest  # type: ignore
import sys
sys.path.insert(0, r'D:\bhaiya test')

from src.game_engine import GameEngine  # type: ignore
from src.player import Player  # type: ignore


class TestGameEngineInit:
    """Test game engine initialization."""
    
    def test_create_game_with_2_players(self):
        engine = GameEngine(2)
        assert len(engine.players) == 2
        assert engine.game_over == False
        assert engine.winner is None
    
    def test_create_game_with_4_players(self):
        engine = GameEngine(4)
        assert len(engine.players) == 4
    
    def test_invalid_player_count_too_low(self):
        with pytest.raises(ValueError):
            GameEngine(1)
    
    def test_invalid_player_count_too_high(self):
        with pytest.raises(ValueError):
            GameEngine(5)
    
    def test_players_start_at_position_0(self):
        engine = GameEngine(3)
        for player in engine.players:
            assert player.position == 0
    
    def test_player_1_starts(self):
        engine = GameEngine(2)
        assert engine.get_current_player().id == 1


class TestTurnManagement:
    """Test turn management."""
    
    def test_turn_rotates_players(self):
        engine = GameEngine(3, seed=42)
        
        # Player 1's turn
        assert engine.get_current_player().id == 1
        engine.do_turn(1)
        
        # Player 2's turn
        assert engine.get_current_player().id == 2
        engine.do_turn(1)
        
        # Player 3's turn
        assert engine.get_current_player().id == 3
        engine.do_turn(1)
        
        # Back to Player 1
        assert engine.get_current_player().id == 1
    
    def test_turn_count_increments(self):
        engine = GameEngine(2, seed=42)
        assert engine.turn_count == 0
        engine.do_turn(1)
        assert engine.turn_count == 1
        engine.do_turn(1)
        assert engine.turn_count == 2


class TestMovement:
    """Test player movement."""
    
    def test_player_moves_by_dice_value(self):
        engine = GameEngine(2, seed=42)
        result = engine.do_turn(5)
        assert result["dice"] == 5
        assert result["new_position"] == 5
    
    def test_invalid_dice_value(self):
        engine = GameEngine(2)
        result = engine.do_turn(7)
        assert "error" in result
    
    def test_invalid_dice_value_zero(self):
        engine = GameEngine(2)
        result = engine.do_turn(0)
        assert "error" in result


class TestWinCondition:
    """Test win detection."""
    
    def test_win_when_passing_30(self):
        engine = GameEngine(2, seed=42)
        
        # Move player 1 to position 28
        engine.players[0].move(28)
        
        # Roll 6 to pass 30
        result = engine.do_turn(6)
        
        assert result["game_over"] == True
        assert result["winner"] == 1
        assert engine.game_over == True
        assert engine.winner.id == 1
    
    def test_no_win_at_exactly_30(self):
        engine = GameEngine(2, seed=42)
        engine.players[0].move(25)
        result = engine.do_turn(5)  # Land on exactly 30
        
        assert result["new_position"] == 30
        assert result["game_over"] == False
    
    def test_no_turns_after_game_over(self):
        engine = GameEngine(2)
        engine.players[0].move(30)
        engine.do_turn(1)  # Player 1 wins
        
        result = engine.do_turn(1)
        assert "error" in result


class TestSkipTurn:
    """Test skip turn mechanics."""
    
    def test_skip_turn_effect(self):
        engine = GameEngine(2, seed=42)
        
        # Set player 1 to skip
        engine.players[0].set_skip_turn()
        
        result = engine.do_turn(5)
        assert result["skipped"] == True
        assert result["player"] == 1
        
        # Next turn is still player 2
        assert engine.get_current_player().id == 2


class TestGameState:
    """Test game state retrieval."""
    
    def test_get_game_state(self):
        engine = GameEngine(3, seed=42)
        engine.do_turn(3)
        
        state = engine.get_game_state()
        
        assert state["turn_count"] == 1
        assert state["current_player"] == 2
        assert len(state["players"]) == 3
        assert "special_fields" in state
        assert state["game_over"] == False
    
    def test_turn_log(self):
        engine = GameEngine(2, seed=42)
        engine.do_turn(2)
        engine.do_turn(3)
        
        log = engine.get_turn_log()
        assert len(log) == 2
        assert log[0]["dice"] == 2
        assert log[1]["dice"] == 3

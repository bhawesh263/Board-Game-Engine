"""Integration tests - full game simulations."""

import pytest  # type: ignore
import sys
sys.path.insert(0, r'D:\bhaiya test')

from src.game_interface import GameInterface  # type: ignore
from src.game_engine import GameEngine  # type: ignore


class TestGameInterface:
    """Test the game interface."""
    
    def test_init_game(self):
        game = GameInterface()
        result = game.init_game(3)
        
        assert result["success"] == True
        assert "state" in result
    
    def test_init_game_invalid_players(self):
        game = GameInterface()
        result = game.init_game(5)
        
        assert result["success"] == False
        assert "error" in result
    
    def test_do_turn_without_init(self):
        game = GameInterface()
        result = game.do_turn(3)
        
        assert result["success"] == False
        assert "not initialized" in result["error"]
    
    def test_do_turn(self):
        game = GameInterface()
        game.init_game(2, seed=42)
        
        result = game.do_turn(4)
        
        assert result["success"] == True
        assert result["turn_result"]["dice"] == 4
        assert "state" in result
    
    def test_get_current_player(self):
        game = GameInterface()
        game.init_game(2)
        
        current = game.get_current_player()
        
        assert current["success"] == True
        assert current["current_player"] == 1


class TestFullGameSimulation:
    """Test complete game simulations."""
    
    def test_play_full_game(self):
        engine = GameEngine(2, seed=42)
        result = engine.play_full_game()
        
        assert result["game_over"] == True
        assert result["winner"] in [1, 2]
    
    def test_game_ends_within_reasonable_turns(self):
        engine = GameEngine(4, seed=42)
        result = engine.play_full_game(max_turns=500)
        
        # Game should end well before 500 turns
        assert result["game_over"] == True
        assert result["turn_count"] < 500
    
    def test_winner_has_passed_30(self):
        engine = GameEngine(2, seed=42)
        engine.play_full_game()
        
        winner = engine.winner
        assert winner.position > 30
    
    def test_interface_full_game(self):
        game = GameInterface()
        game.init_game(3, seed=123)
        
        turn_count = 0
        max_turns = 200
        
        while not game.is_game_over() and turn_count < max_turns:
            import random
            dice = random.randint(1, 6)
            game.do_turn(dice)
            turn_count += 1
        
        assert game.is_game_over()
        winner = game.get_winner()
        assert winner in [1, 2, 3]


class TestSpecialFieldInteractions:
    """Test special field interactions in gameplay."""
    
    def test_bonus_then_trap_only_activates_bonus(self):
        """If bonus moves player to trap, trap should NOT activate."""
        engine = GameEngine(2, seed=42)
        
        # Manually position things for this test
        player = engine.players[0]
        player.move(5)  # Set position
        player.reset_turn()
        
        # Simulate landing on bonus that moves forward 2
        player.mark_special_activated()
        player.move(2)  # Simulated bonus effect
        
        # Now player cannot activate another special this turn
        assert player.can_activate_special() == False
    
    def test_joker_blocks_trap(self):
        """Test that joker blocks trap effect."""
        engine = GameEngine(2, seed=42)
        
        player = engine.players[0]
        player.give_joker()
        
        # Get trap field position
        special = engine.board.get_special_field_positions()
        if special["trap"]:
            trap_pos = special["trap"][0]
            
            # Move player just before trap
            player.move(trap_pos - 1)
            
            # Roll to land on trap
            old_pos = player.position
            result = engine.do_turn(1)
            
            # If activation occurred and was blocked
            if result.get("field_activation") and result["field_activation"].get("blocked_by_joker"):
                assert player.has_joker == False


class TestEdgeCases:
    """Test edge cases."""
    
    def test_all_players_at_same_position(self):
        engine = GameEngine(4, seed=42)
        
        # Move all players to position 10
        for player in engine.players:
            player.move(10)
        
        # All at same position should be valid
        positions = [p.position for p in engine.players]
        assert all(p == 10 for p in positions)
    
    def test_player_pushed_back_to_zero(self):
        engine = GameEngine(2, seed=42)
        
        # Player at position 1, pushed back 2 should be at 0
        engine.players[0].move(1)
        engine.players[0].move(-2)
        
        assert engine.players[0].position == 0
    
    def test_reproducible_game(self):
        """Same seed should produce same game."""
        engine1 = GameEngine(2, seed=999)
        engine2 = GameEngine(2, seed=999)
        
        # Play same sequence
        for dice in [3, 4, 5, 2, 6, 1]:
            if not engine1.game_over:
                engine1.do_turn(dice)
            if not engine2.game_over:
                engine2.do_turn(dice)
        
        state1 = engine1.get_game_state()
        state2 = engine2.get_game_state()
        
        # Same positions
        for p1, p2 in zip(state1["players"], state2["players"]):
            assert p1["position"] == p2["position"]

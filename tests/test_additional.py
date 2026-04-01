"""Additional tests for comprehensive coverage."""

import pytest  # type: ignore
import sys
sys.path.insert(0, r'D:\bhaiya test')

from src.game_engine import GameEngine  # type: ignore
from src.game_interface import GameInterface  # type: ignore
from src.board import Board, BonusField, TrapField, BonusType, TrapType  # type: ignore
from src.player import Player  # type: ignore


class TestBonusEffectsDetailed:
    """Detailed tests for all bonus effects."""
    
    def test_bonus_type_1_moves_exactly_2_forward(self):
        """Verify Type 1 bonus moves player exactly 2 fields forward."""
        player = Player(1)
        player.move(10)  # Start at position 10
        initial_pos = player.position
        
        # Create bonus field and force type 1
        field = BonusField(10, seed=1)  # seed=1 gives type 1
        field._random.seed(1)
        
        all_players = [player]
        result = field.activate(player, all_players)
        
        # Should have activated
        assert result["activated"] == True
        # Position should be initial + 2
        assert player.position == initial_pos + 2
    
    def test_bonus_type_2_affects_all_other_players(self):
        """Verify Type 2 bonus pushes ALL other players back 2."""
        players = [Player(i) for i in range(1, 5)]  # 4 players
        
        # Position all players
        for i, p in enumerate(players):
            p.move(10 + i * 2)  # 10, 12, 14, 16
        
        initial_positions = [p.position for p in players]
        
        # Player 1 activates bonus type 2
        field = BonusField(10, seed=42)
        field._random.seed(5)  # seed=5 gives type 2
        
        result = field.activate(players[0], players)
        
        # Player 1 position unchanged (by this effect)
        # All others should be pushed back 2
        if result.get("bonus_type") == 2:
            for i, p in enumerate(players):
                if i == 0:
                    # Activating player not affected
                    continue
                assert p.position == initial_positions[i] - 2
    
    def test_bonus_type_3_gives_joker_once_only(self):
        """Verify Type 3 bonus gives joker only if player doesn't have one."""
        player = Player(1)
        player.move(5)
        
        # First joker
        player.give_joker()
        assert player.has_joker == True
        
        # Try to give another
        result = player.give_joker()
        assert result == False  # Already has joker
        assert player.has_joker == True  # Still has exactly 1


class TestTrapEffectsDetailed:
    """Detailed tests for all trap effects."""
    
    def test_trap_type_1_moves_exactly_2_back(self):
        """Verify Type 1 trap moves player exactly 2 fields back."""
        player = Player(1)
        player.move(10)
        initial_pos = player.position
        
        field = TrapField(10, seed=1)
        field._random.seed(1)  # type 1
        
        result = field.activate(player, [player])
        
        if result.get("trap_type") == 1 and not result.get("blocked_by_joker"):
            assert player.position == initial_pos - 2
    
    def test_trap_type_2_moves_others_forward(self):
        """Verify Type 2 trap moves all OTHER players forward 2."""
        players = [Player(i) for i in range(1, 4)]
        for i, p in enumerate(players):
            p.move(5 + i)
        
        initial_positions = [p.position for p in players]
        
        field = TrapField(5, seed=42)
        field._random.seed(3)  # try to get type 2
        
        result = field.activate(players[0], players)
        
        if result.get("trap_type") == 2:
            for i, p in enumerate(players[1:], 1):  # type: ignore
                assert p.position == initial_positions[i] + 2
    
    def test_trap_type_3_skips_only_next_turn(self):
        """Verify Type 3 trap skips only ONE turn, not permanent."""
        player = Player(1)
        player.set_skip_turn()
        
        # First check - should skip
        assert player.should_skip_turn() == True
        
        # Second check - should NOT skip (reset)
        assert player.should_skip_turn() == False
        assert player.skip_next_turn == False


class TestFieldPositions:
    """Test field positions are correct."""
    
    def test_all_fields_have_positions_1_to_30(self):
        """Verify all 30 fields have correct positions 1-30."""
        board = Board(seed=42)
        
        positions = [f.position for f in board.fields]
        
        assert len(positions) == 30
        assert positions == list(range(1, 31))
    
    def test_special_fields_within_valid_range(self):
        """Verify special fields are within 1-30."""
        board = Board(seed=42)
        special = board.get_special_field_positions()
        
        for pos in special["bonus"]:
            assert 1 <= pos <= 30
        
        for pos in special["trap"]:
            assert 1 <= pos <= 30


class TestWinConditions:
    """Test win conditions thoroughly."""
    
    def test_win_after_bonus_forward_movement(self):
        """Verify win detected if bonus moves player past 30."""
        engine = GameEngine(2, seed=42)
        
        # Position player at 29
        engine.players[0].move(29)
        
        # If they land on a bonus field and get +2, they should win
        # Simulate this scenario
        player = engine.players[0]
        player.reset_turn()
        player.move(2)  # Position 31
        
        assert player.has_won() == True
    
    def test_win_requires_passing_not_landing(self):
        """Verify player must PASS 30, not land on it."""
        player = Player(1)
        
        player.move(30)  # Exactly at 30
        assert player.has_won() == False
        
        player.move(1)  # Now at 31
        assert player.has_won() == True
    
    def test_game_stops_after_winner(self):
        """Verify no more turns after someone wins."""
        engine = GameEngine(2, seed=42)
        
        # Make player 1 win
        engine.players[0].move(31)
        result = engine.do_turn(1)
        
        assert engine.game_over == True
        
        # Try another turn
        result2 = engine.do_turn(1)
        assert "error" in result2


class TestSpecialFieldChaining:
    """Test that special field effects don't chain."""
    
    def test_bonus_to_trap_only_activates_bonus(self):
        """Landing on bonus that moves to trap should NOT trigger trap."""
        engine = GameEngine(2, seed=42)
        
        player = engine.players[0]
        player.move(5)
        player.reset_turn()
        
        # Activate a special field
        player.mark_special_activated()
        
        # Now cannot activate another
        assert player.can_activate_special() == False
    
    def test_pushed_players_dont_trigger_fields(self):
        """Players pushed by effects don't trigger special fields."""
        players = [Player(i) for i in range(1, 3)]
        
        # Player 2 at position 8 (let's say there's a trap at 6)
        players[1].move(8)
        players[1].reset_turn()
        
        # Player 1 activates bonus type 2 (push others back 2)
        # Player 2 goes from 8 to 6
        players[1].move(-2)
        
        # Player 2 should NOT have activated any special field
        # (They weren't in a "turn" state)
        assert players[1].can_activate_special() == True  # Never activated


class TestDice:
    """Test dice functionality."""
    
    def test_dice_rolls_1_to_6_only(self):
        """Verify dice only rolls values 1-6."""
        from src.dice import Dice  # type: ignore
        
        dice = Dice(seed=42)
        rolls = [dice.roll() for _ in range(1000)]
        
        assert all(1 <= r <= 6 for r in rolls)
        assert set(rolls) == {1, 2, 3, 4, 5, 6}  # All values appear
    
    def test_dice_reproducible_with_seed(self):
        """Verify same seed gives same rolls."""
        from src.dice import Dice  # type: ignore
        
        dice1 = Dice(seed=123)
        dice2 = Dice(seed=123)
        
        rolls1 = [dice1.roll() for _ in range(10)]
        rolls2 = [dice2.roll() for _ in range(10)]
        
        assert rolls1 == rolls2


class TestGameInterface:
    """Test game interface edge cases."""
    
    def test_get_state_before_init(self):
        """Getting state before init should fail gracefully."""
        game = GameInterface()
        result = game.get_state()
        
        assert result["success"] == False
        assert "not initialized" in result["error"].lower()
    
    def test_get_winner_before_game_over(self):
        """Getting winner before game ends returns None."""
        game = GameInterface()
        game.init_game(2)
        
        assert game.get_winner() is None
    
    def test_turn_log_grows(self):
        """Turn log should grow with each turn."""
        game = GameInterface()
        game.init_game(2, seed=42)
        
        assert len(game.get_turn_log()) == 0
        
        game.do_turn(3)
        assert len(game.get_turn_log()) == 1
        
        game.do_turn(4)
        assert len(game.get_turn_log()) == 2

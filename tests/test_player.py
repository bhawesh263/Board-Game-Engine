"""Unit tests for Player class."""

import pytest  # type: ignore
import sys
sys.path.insert(0, r'D:\bhaiya test')

from src.player import Player  # type: ignore


class TestPlayerInit:
    """Test player initialization."""
    
    def test_create_player(self):
        player = Player(1)
        assert player.id == 1
        assert player.position == 0
        assert player.has_joker == False
        assert player.skip_next_turn == False
    
    def test_create_multiple_players(self):
        players = [Player(i) for i in range(1, 5)]
        assert len(players) == 4
        for i, p in enumerate(players):
            assert p.id == i + 1


class TestPlayerMovement:
    """Test player movement."""
    
    def test_move_forward(self):
        player = Player(1)
        new_pos = player.move(5)
        assert new_pos == 5
        assert player.position == 5
    
    def test_move_multiple_times(self):
        player = Player(1)
        player.move(3)
        player.move(4)
        assert player.position == 7
    
    def test_move_backward(self):
        player = Player(1)
        player.move(10)
        player.move(-3)
        assert player.position == 7
    
    def test_move_backward_not_below_zero(self):
        player = Player(1)
        player.move(2)
        player.move(-5)
        assert player.position == 0


class TestPlayerJoker:
    """Test joker mechanics."""
    
    def test_give_joker(self):
        player = Player(1)
        assert player.give_joker() == True
        assert player.has_joker == True
    
    def test_give_joker_when_already_has_one(self):
        player = Player(1)
        player.give_joker()
        assert player.give_joker() == False
        assert player.has_joker == True
    
    def test_use_joker(self):
        player = Player(1)
        player.give_joker()
        assert player.use_joker() == True
        assert player.has_joker == False
    
    def test_use_joker_when_none(self):
        player = Player(1)
        assert player.use_joker() == False


class TestPlayerSkipTurn:
    """Test skip turn mechanics."""
    
    def test_set_skip_turn(self):
        player = Player(1)
        player.set_skip_turn()
        assert player.skip_next_turn == True
    
    def test_should_skip_turn_resets_flag(self):
        player = Player(1)
        player.set_skip_turn()
        assert player.should_skip_turn() == True
        assert player.skip_next_turn == False
        assert player.should_skip_turn() == False


class TestPlayerSpecialActivation:
    """Test special field activation tracking."""
    
    def test_can_activate_special_initially(self):
        player = Player(1)
        assert player.can_activate_special() == True
    
    def test_mark_special_activated(self):
        player = Player(1)
        player.mark_special_activated()
        assert player.can_activate_special() == False
    
    def test_reset_turn_clears_activation(self):
        player = Player(1)
        player.mark_special_activated()
        player.reset_turn()
        assert player.can_activate_special() == True


class TestPlayerWin:
    """Test win condition."""
    
    def test_has_won_when_past_30(self):
        player = Player(1)
        player.move(31)
        assert player.has_won() == True
    
    def test_has_not_won_at_30(self):
        player = Player(1)
        player.move(30)
        assert player.has_won() == False
    
    def test_has_not_won_before_30(self):
        player = Player(1)
        player.move(25)
        assert player.has_won() == False

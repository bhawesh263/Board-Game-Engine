"""2D Board Visualization using Matplotlib with GUI controls and animations."""

import matplotlib.pyplot as plt  # type: ignore
import matplotlib.patches as patches  # type: ignore
from matplotlib.widgets import Button  # type: ignore
import numpy as np  # type: ignore
from typing import List, Dict, Any
import random


class BoardGame:
    """2D board game with full GUI controls and animated effects."""
    
    COLORS = {
        'normal': '#E0E0E0',
        'bonus': '#7FD37F',
        'trap': '#FF8A8A',
        'player1': '#3366CC',
        'player2': '#DC3545',
        'player3': '#28A745',
        'player4': '#FF8C00',
        'highlight': '#FFD700',
        'bg': '#F5F5F5'
    }
    
    BONUS_DESCRIPTIONS = {
        1: "Move Forward +2",
        2: "Push Others Back -2",
        3: "Got a Joker!"
    }
    
    TRAP_DESCRIPTIONS = {
        1: "Move Back -2",
        2: "Others Move +2",
        3: "Skip Next Turn!"
    }
    
    def __init__(self, num_players: int):
        """Initialize the game."""
        import sys
        import os
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
            
        from src.game_interface import GameInterface  # type: ignore
        
        self.game = GameInterface()
        self.game.init_game(num_players)
        self.num_players = num_players
        
        state = self.game.get_state()['state']
        self.bonus_fields = state['special_fields']['bonus']
        self.trap_fields = state['special_fields']['trap']
        
        self.fig: Any = None
        self.ax: Any = None
        self.buttons: Dict[str, Any] = {}
        self.status_text: Any = None
        self.message = ""
        self.game_ended = False
        self.auto_playing = False  # Track auto-play state
        self._auto_timer: Any = None    # Matplotlib timer for auto-play
        
    def _get_field_position(self, field_num: int) -> tuple:
        """Convert field number (1-30) to x,y coordinates - snakes & ladders style."""
        if field_num <= 0:
            return (-1.5, 0.5)  # Start at bottom
        if field_num > 30:
            return (11.5, 2.5)  # Finish at top
            
        # Snakes and ladders: 1 at bottom-left, 30 at top
        row = (field_num - 1) // 10  # 0, 1, 2
        col = (field_num - 1) % 10   # 0-9
        
        # Reverse direction on odd rows (snake pattern)
        if row % 2 == 1:
            col = 9 - col
            
        x = col + 0.5
        y = row + 0.5  # Row 0 at bottom, row 2 at top
        return (x, y)
    
    def _draw_board(self):
        """Draw the game board."""
        self.ax.clear()
        self.ax.set_xlim(-2.5, 12.5)
        self.ax.set_ylim(-1, 4.5)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        self.ax.set_facecolor(self.COLORS['bg'])
        
        # Title
        self.ax.text(5, 4.0, 'BOARD GAME', ha='center', va='center',
                    fontsize=20, fontweight='bold', color='#333')
        
        # Draw fields
        for i in range(1, 31):
            x, y = self._get_field_position(i)
            
            if i in self.bonus_fields:
                color = self.COLORS['bonus']
                symbol = 'B'
            elif i in self.trap_fields:
                color = self.COLORS['trap']
                symbol = 'T'
            else:
                color = self.COLORS['normal']
                symbol = ''
            
            # Field background
            rect = patches.FancyBboxPatch(
                (x - 0.45, y - 0.45), 0.9, 0.9,
                boxstyle="round,pad=0.03",
                facecolor=color, edgecolor='#333', linewidth=2
            )
            self.ax.add_patch(rect)
            
            # Field number
            self.ax.text(x, y + 0.1, str(i), ha='center', va='center',
                        fontsize=11, fontweight='bold', color='#333')
            
            # Symbol for special fields
            if symbol:
                self.ax.text(x, y - 0.25, symbol, ha='center', va='center',
                            fontsize=8)
        
        # START area (bottom left)
        start_rect = patches.FancyBboxPatch(
            (-2.2, -0.2), 1.4, 1.4,
            boxstyle="round,pad=0.05",
            facecolor='#90EE90', edgecolor='#228B22', linewidth=3
        )
        self.ax.add_patch(start_rect)
        self.ax.text(-1.5, 0.5, 'S', ha='center', va='center', fontsize=20, fontweight='bold')
        self.ax.text(-1.5, 0.0, 'START', ha='center', va='center',
                    fontsize=10, fontweight='bold', color='#228B22')
        
        # FINISH area (top right)
        finish_rect = patches.FancyBboxPatch(
            (10.8, 1.8), 1.4, 1.4,
            boxstyle="round,pad=0.05",
            facecolor='#FFD700', edgecolor='#FF6600', linewidth=3
        )
        self.ax.add_patch(finish_rect)
        self.ax.text(11.5, 2.5, 'W', ha='center', va='center', fontsize=20, fontweight='bold')
        self.ax.text(11.5, 2.0, 'FINISH', ha='center', va='center',
                    fontsize=10, fontweight='bold', color='#FF6600')
        
        # Draw players
        state = self.game.get_state()['state']
        positions = [p['position'] for p in state['players']]
        current_player = 0
        if not state['game_over']:
            current_player = self.game.get_current_player()['current_player']
        
        offsets = [(-0.22, 0.22), (0.22, 0.22), (-0.22, -0.18), (0.22, -0.18)]
        
        for i, pos in enumerate(positions):
            x, y = self._get_field_position(pos)
            offset = offsets[i] if i < len(offsets) else (0, 0)
            
            is_current = (i + 1 == current_player)
            size = 450 if is_current else 320
            edge = '#FFD700' if is_current else '#333'
            lw = 4 if is_current else 2
            
            # Player circle
            self.ax.scatter(x + offset[0], y + offset[1], 
                          c=self.COLORS[f'player{i+1}'],
                          s=size, edgecolors=edge, linewidths=lw, zorder=10)
            
            # Player number
            self.ax.text(x + offset[0], y + offset[1], str(i+1),
                        ha='center', va='center', color='white',
                        fontsize=11, fontweight='bold', zorder=11)
        
        # Player info panel (on left side, vertical layout)
        panel_x = -2.3
        self.ax.text(panel_x, 3.5, 'PLAYERS', ha='left', va='center',
                    fontsize=12, fontweight='bold', color='#333')
        
        for i in range(self.num_players):
            info = state['players'][i]
            y_pos = 3.1 - i * 0.55
            
            is_current = (i + 1 == current_player)
            
            # Background for current player
            if is_current:
                bg_rect = patches.FancyBboxPatch(
                    (panel_x - 0.1, y_pos - 0.2), 2.0, 0.45,
                    boxstyle="round,pad=0.02",
                    facecolor='#FFFACD', edgecolor='#FFD700', linewidth=2
                )
                self.ax.add_patch(bg_rect)
            
            # Player color dot
            self.ax.scatter(panel_x + 0.15, y_pos, c=self.COLORS[f'player{i+1}'],
                          s=150, edgecolors='#333', linewidths=1, zorder=5)
            self.ax.text(panel_x + 0.15, y_pos, str(i+1), ha='center', va='center',
                        color='white', fontsize=9, fontweight='bold', zorder=6)
            
            # Position text
            self.ax.text(panel_x + 0.45, y_pos, f'Field {info["position"]:2d}',
                        ha='left', va='center', fontsize=10, fontweight='bold')
            
            # Status icons
            status_x = panel_x + 1.4
            if info['has_joker']:
                self.ax.text(status_x, y_pos, 'J', ha='center', va='center', fontsize=10, fontweight='bold')
                status_x += 0.25
            if info['skip_next_turn']:
                self.ax.text(status_x, y_pos, 'SKIP', ha='center', va='center', fontsize=8, fontweight='bold')
        
        # Legend (bottom right)
        legend_x = 9.5
        legend_y = -0.7
        
        # Bonus legend
        self.ax.add_patch(patches.Rectangle((legend_x, legend_y), 0.4, 0.35,
                         facecolor=self.COLORS['bonus'], edgecolor='#333', linewidth=1))
        self.ax.text(legend_x + 0.2, legend_y + 0.17, 'B', ha='center', va='center', fontsize=8, fontweight='bold')
        self.ax.text(legend_x + 0.55, legend_y + 0.17, 'Bonus', ha='left', va='center', fontsize=10)
        
        # Trap legend
        self.ax.add_patch(patches.Rectangle((legend_x + 2, legend_y), 0.4, 0.35,
                         facecolor=self.COLORS['trap'], edgecolor='#333', linewidth=1))
        self.ax.text(legend_x + 2.2, legend_y + 0.17, 'T', ha='center', va='center', fontsize=8, fontweight='bold')
        self.ax.text(legend_x + 2.55, legend_y + 0.17, 'Trap', ha='left', va='center', fontsize=10)
    
    def _show_fireworks(self):
        """Show fireworks/confetti animation for winner."""
        colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF', 
                  '#FFA500', '#FF69B4', '#FFD700', '#7FFF00']
        
        # Create multiple bursts of fireworks
        for burst in range(3):
            # Random firework particles
            for _ in range(50):
                x = random.uniform(0, 10)
                y = random.uniform(0, 3)
                color = random.choice(colors)
                size = random.uniform(50, 200)
                marker = random.choice(['*', 'o', '^', 's', 'p', 'h'])
                self.ax.scatter(x, y, c=color, s=size, marker=marker, 
                              alpha=0.8, zorder=150)
            
            # Firework emojis
            firework_emojis = ['*', '+', 'x', 'o', '.', '^']
            for _ in range(15):
                x = random.uniform(-1, 11)
                y = random.uniform(-0.5, 3.5)
                emoji = random.choice(firework_emojis)
                self.ax.text(x, y, emoji, fontsize=random.randint(15, 30),
                           ha='center', va='center', zorder=151)
            
            self.fig.canvas.draw_idle()
            self.fig.canvas.flush_events()
            plt.pause(0.4)
            
            # Redraw board for next burst (keeps fireworks layered)
            if burst < 2:
                self._draw_board()
    
    def _show_popup(self, popup_type: str, title: str, description: str):
        """Show animated popup for bonus/trap."""
        # Colors based on type
        if popup_type == 'bonus':
            bg_color = '#4CAF50'
            border_color = '#2E7D32'
            emoji = '[BONUS]'
        elif popup_type == 'trap':
            bg_color = '#F44336'
            border_color = '#C62828'
            emoji = '[TRAP]'
        elif popup_type == 'joker':
            bg_color = '#9C27B0'
            border_color = '#6A1B9A'
            emoji = '[JOKER]'
        else:  # winner
            bg_color = '#FFD700'
            border_color = '#FF8C00'
            emoji = '[WINNER]'
        
        # Create popup
        popup_rect = patches.FancyBboxPatch(
            (2.5, 1.0), 5, 1.8,
            boxstyle="round,pad=0.1",
            facecolor=bg_color, edgecolor=border_color, 
            linewidth=4, alpha=0.95, zorder=100
        )
        self.ax.add_patch(popup_rect)
        
        # Popup content
        self.ax.text(5, 2.3, f'{emoji} {title} {emoji}', ha='center', va='center',
                    fontsize=16, fontweight='bold', color='white', zorder=101)
        self.ax.text(5, 1.6, description, ha='center', va='center',
                    fontsize=13, color='white', zorder=101,
                    style='italic')
        
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()
        
        # Auto-hide after delay
        plt.pause(1.5)
    
    def _update_display(self):
        """Update the display."""
        self._draw_board()
        
        if self.status_text:
            self.status_text.set_text(self.message)
        
        self.fig.canvas.draw_idle()
    
    def _roll_dice(self, value: int):
        """Execute a dice roll."""
        if self.game_ended:
            return
            
        result = self.game.do_turn(value)
        
        if result['success']:
            turn = result['turn_result']
            state = result['state']
            
            if turn.get('skipped'):
                self.message = f"Player {turn['player']} skipped turn!"
                self._update_display()
            else:
                self.message = f"Player {turn['player']} rolled {turn['dice']}: {turn['old_position']} → {turn['new_position']}"
                self._update_display()
                
                # Check for special field activation
                if turn.get('field_activation') and turn['field_activation'].get('activated'):
                    act = turn['field_activation']
                    
                    if act.get('blocked_by_joker'):
                        self._show_popup('joker', 'JOKER USED!', 'Trap was blocked!')
                        self.message += " | Joker blocked trap!"
                    else:
                        ftype = act.get('field_type', '')
                        
                        if ftype == 'bonus':
                            bonus_type = act.get('bonus_type', 1)
                            desc = self.BONUS_DESCRIPTIONS.get(bonus_type, 'Bonus!')
                            self._show_popup('bonus', f'BONUS TYPE {bonus_type}', desc)
                            self.message += f" | BONUS: {desc}"
                        elif ftype == 'trap':
                            trap_type = act.get('trap_type', 1)
                            desc = self.TRAP_DESCRIPTIONS.get(trap_type, 'Trap!')
                            self._show_popup('trap', f'TRAP TYPE {trap_type}', desc)
                            self.message += f" | TRAP: {desc}"
                
                self._update_display()
            
            if state['game_over']:
                self.game_ended = True
                self._show_fireworks()  # Show fireworks first!
                self._show_popup('winner', f'PLAYER {state["winner"]} WINS!', 'Congratulations!')
                self.message = f"PLAYER {state['winner']} WINS!"
                self._update_display()
                
                # Disable dice buttons
                for btn in self.buttons.values():
                    btn.color = 'lightgray'
                    btn.hovercolor = 'lightgray'
    
    def _on_dice_click(self, event, value):
        """Handle dice button click."""
        self._roll_dice(value)
    
    def _on_random_click(self, event):
        """Handle random roll button click."""
        self._roll_dice(random.randint(1, 6))
    
    def _stop_auto_timer(self):
        """Stop the auto-play timer if running."""
        if self._auto_timer is not None:
            self._auto_timer.stop()
            self._auto_timer = None

    def _on_auto_toggle(self, event):
        """Toggle auto-play on/off."""
        if self.game_ended:
            return
        
        if self.auto_playing:
            # Stop auto-play
            self.auto_playing = False
            self._stop_auto_timer()
            self.buttons['auto'].label.set_text('AUTO')
            self.buttons['auto'].color = '#FF9800'
            self.buttons['auto'].hovercolor = '#EF6C00'
            self.message = "Auto-play stopped. Click dice to play!"
            self._update_display()
        else:
            # Start auto-play
            self.auto_playing = True
            self.buttons['auto'].label.set_text('STOP')
            self.buttons['auto'].color = '#F44336'
            self.buttons['auto'].hovercolor = '#D32F2F'
            
            def auto_step(*args):
                if not self.game_ended and self.auto_playing:
                    self._roll_dice(random.randint(1, 6))
                if not self.auto_playing or self.game_ended:
                    self._stop_auto_timer()
                    if not self.game_ended:
                        self.buttons['auto'].label.set_text('AUTO')
                        self.buttons['auto'].color = '#FF9800'
                        self.buttons['auto'].hovercolor = '#EF6C00'
            
            self._stop_auto_timer()
            self._auto_timer = self.fig.canvas.new_timer(interval=800)
            self._auto_timer.add_callback(auto_step)
            self._auto_timer.start()
    
    def _on_auto_click(self, event):
        """Handle auto-play button click."""
        if self.game_ended or self.auto_playing:
            return
        self._on_auto_toggle(event)
    
    def _on_stop_click(self, event):
        """Handle stop button click to stop auto-play."""
        if self.auto_playing:
            self.auto_playing = False
            self._stop_auto_timer()
            self.buttons['auto'].label.set_text('AUTO')
            self.buttons['auto'].color = '#FF9800'
            self.buttons['auto'].hovercolor = '#EF6C00'
            self.message = "Auto-play stopped. Your turn!"
            self._update_display()
    
    def run(self):
        """Run the game with GUI."""
        # Create figure
        self.fig, self.ax = plt.subplots(figsize=(15, 10))
        self.fig.patch.set_facecolor('#F0F0F0')
        self.fig.canvas.manager.set_window_title('Board Game - 2D Simulation')
        plt.subplots_adjust(bottom=0.15, top=0.95, left=0.02, right=0.98)
        
        # Create dice buttons
        btn_width = 0.07
        btn_height = 0.055
        btn_y = 0.05
        start_x = 0.18
        
        dice_emojis = ['⚀', '⚁', '⚂', '⚃', '⚄', '⚅']
        
        for i in range(1, 7):
            ax_btn = plt.axes([start_x + (i-1)*0.09, btn_y, btn_width, btn_height])
            btn = Button(ax_btn, f'{dice_emojis[i-1]} {i}', color='#4CAF50', hovercolor='#388E3C')
            btn.label.set_fontsize(13)
            btn.label.set_fontweight('bold')
            btn.label.set_color('white')
            btn.on_clicked(lambda event, v=i: self._on_dice_click(event, v))
            self.buttons[f'dice_{i}'] = btn
        
        # Random roll button
        ax_random = plt.axes([0.74, btn_y, 0.1, btn_height])
        btn_random = Button(ax_random, 'ROLL', color='#2196F3', hovercolor='#1565C0')
        btn_random.label.set_fontsize(12)
        btn_random.label.set_fontweight('bold')
        btn_random.label.set_color('white')
        btn_random.on_clicked(self._on_random_click)
        self.buttons['random'] = btn_random
        
        # Auto-play button (toggles to STOP when active)
        ax_auto = plt.axes([0.85, btn_y, 0.1, btn_height])
        btn_auto = Button(ax_auto, 'AUTO', color='#FF9800', hovercolor='#EF6C00')
        btn_auto.label.set_fontsize(12)
        btn_auto.label.set_fontweight('bold')
        btn_auto.label.set_color('white')
        btn_auto.on_clicked(self._on_auto_toggle)
        self.buttons['auto'] = btn_auto
        
        # Status text
        self.status_text = self.fig.text(0.5, 0.115, 'Click a dice button to play!', 
                                         fontsize=13, ha='center', fontweight='bold',
                                         color='#333', 
                                         bbox=dict(boxstyle='round,pad=0.3', 
                                                  facecolor='white', edgecolor='#DDD'))
        
        # Initial draw
        self._draw_board()
        
        # Show
        plt.show()


def run_visual_game():
    """Run the game with 2D visualization."""
    print("=" * 50)
    print("BOARD GAME - 2D Visual Simulation")
    print("=" * 50)
    
    # Get number of players
    while True:
        try:
            num_players = int(input("\nEnter number of players (2-4): "))
            if 2 <= num_players <= 4:
                break
            print("Please enter a number between 2 and 4.")
        except ValueError:
            print("Please enter a valid number.")
    
    print("\nStarting game...")
    print("\nControls (in game window):")
    print("  1-6   : Click to roll specific number")
    print("  ROLL  : Random dice roll")
    print("  AUTO  : Watch auto-play (toggle with STOP)")
    print("\nBonus Types:")
    print("  Type 1: Move Forward +2")
    print("  Type 2: Push Others Back -2")
    print("  Type 3: Get a Joker (blocks next trap)")
    print("\nTrap Types:")
    print("  Type 1: Move Back -2")
    print("  Type 2: Others Move Forward +2")
    print("  Type 3: Skip Next Turn")
    
    # Run game
    game = BoardGame(num_players)
    game.run()
    
    print("\nGame closed.")


if __name__ == "__main__":
    run_visual_game()

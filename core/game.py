"""
Main Pong game logic and state management
"""
import time
from core.ball import Ball
from core.paddle import Paddle
import config

class PongGame:
    def __init__(self, width=None, height=None):
        self.width = width or config.SCREEN_WIDTH
        self.height = height or config.SCREEN_HEIGHT
        
        # Game objects
        self.ball = Ball(self.width // 2, self.height // 2)
        self.player_paddle = Paddle(30, self.height // 2 - 40, is_player=True)
        self.ai_paddle = Paddle(self.width - 45, self.height // 2 - 40, is_player=False)
        
        # AI Parameters
        self.ai_error_margin = 0
        self.ai_reaction_delay = 0
        
        # Scoring
        self.player_score = 0
        self.ai_score = 0
        
        # Game state
        self.is_running = True
        self.is_paused = False
        self.frame_count = 0
        self.game_start_time = time.time()
        
        # Rally tracking
        self.current_rally_length = 0
        self.rally_ended = False
        self.ball_direction_changed = False
        self.time_since_direction_change = 0
        self.last_ball_vx = self.ball.vx
    
    def update(self):
        """Update game state"""
        if self.is_paused:
            return
        
        self.frame_count += 1
        self.rally_ended = False
        self.ball_direction_changed = False
        
        # Track ball direction changes
        if (self.ball.vx > 0) != (self.last_ball_vx > 0):
            self.ball_direction_changed = True
            self.time_since_direction_change = 0
        else:
            self.time_since_direction_change += 1 / config.FPS_TARGET
        
        self.last_ball_vx = self.ball.vx
        
        # Update paddles
        self.player_paddle.update(self.height)
        self.ai_paddle.update(self.height)
        
        # Check paddle collisions
        if self.ball.check_paddle_collision(self.player_paddle):
            self.current_rally_length += 1
            self.ball.increase_speed(1.10) # 10% faster per hit (was 5%)
        
        if self.ball.check_paddle_collision(self.ai_paddle):
            self.current_rally_length += 1
            self.ball.increase_speed(1.10) # 10% faster per hit
        
        # Update ball and check scoring
        result = self.ball.update(self.width, self.height)
        
        if result == 'left_scores':
            self.player_score += 1
            self.rally_ended = True
            self.reset_ball()
            return 'player_won'
        elif result == 'right_scores':
            self.ai_score += 1
            self.rally_ended = True
            self.reset_ball()
            return 'ai_won'
            
        return None
    
    def reset_ball(self):
        """Reset ball to center and end rally"""
        self.ball.reset(self.width // 2, self.height // 2)
        self.ball.reset_speed()
        self.current_rally_length = 0
    
    def pause(self):
        """Pause/unpause game"""
        self.is_paused = not self.is_paused
    
    def restart(self):
        """Restart game"""
        self.player_score = 0
        self.ai_score = 0
        self.frame_count = 0
        self.current_rally_length = 0
        self.ball.reset(self.width // 2, self.height // 2)
        self.player_paddle.y = self.height // 2 - 40
        self.ai_paddle.y = self.height // 2 - 40
        self.game_start_time = time.time()

    def set_ai_parameters(self, params):
        """Update AI difficulty parameters"""
        self.ai_paddle.set_speed(params['speed'])
        self.ai_error_margin = params['error_margin']
        self.ai_reaction_delay = params['reaction_delay']
    
    def get_state(self):
        """Get current game state for ML/data collection"""
        return {
            'frame_count': self.frame_count,
            'player_paddle': self.player_paddle,
            'ai_paddle': self.ai_paddle,
            'ball': self.ball,
            'player_score': self.player_score,
            'ai_score': self.ai_score,
            'current_rally_length': self.current_rally_length,
            'rally_ended': self.rally_ended,
            'ball_direction_changed': self.ball_direction_changed,
            'time_since_direction_change': self.time_since_direction_change,
            'status': 'paused' if self.is_paused else 'playing',
            'width': self.width,
            'height': self.height
        }

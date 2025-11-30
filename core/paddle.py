"""
Paddle class for player and AI control
"""
import config

class Paddle:
    def __init__(self, x, y, is_player=True):
        self.x = x
        self.y = y
        self.width = config.PADDLE_WIDTH
        self.height = config.PADDLE_HEIGHT
        self.speed = config.PADDLE_SPEED
        self.target_y = y
        self.is_player = is_player
        self.prev_y = y  # For velocity calculation
    
    def update(self, screen_height):
        """Smooth movement to target position with bounds checking"""
        # Bounds checking for target
        self.target_y = max(0, min(self.target_y, screen_height - self.height))
        
        # Smooth interpolation to target
        diff = self.target_y - self.y
        if abs(diff) > 1:
            # Smooth movement (30% of difference per frame)
            self.y += diff * 0.3
        else:
            self.y = self.target_y
        
        # Ensure paddle stays in bounds
        self.y = max(0, min(self.y, screen_height - self.height))
    
    def set_target(self, y):
        """Set target position for paddle"""
        self.target_y = y
        
    def set_speed(self, speed):
        """Set paddle movement speed"""
        self.speed = speed
    
    def move_up(self):
        """Move paddle up"""
        self.target_y -= self.speed
    
    def move_down(self):
        """Move paddle down"""
        self.target_y += self.speed
    
    def get_velocity(self):
        """Calculate paddle velocity for data collection"""
        velocity = self.y - self.prev_y
        self.prev_y = self.y
        return velocity
    
    def get_center_y(self):
        """Get center Y position of paddle"""
        return self.y + self.height / 2

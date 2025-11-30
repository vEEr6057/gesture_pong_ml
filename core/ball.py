"""
Ball physics and collision detection for Pong game
"""
import config

class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = config.BALL_RADIUS
        self.speed = config.BALL_SPEED
        self.original_speed = config.BALL_SPEED
        self.vx = self.speed
        self.vy = self.speed
        self.reset_count = 0
        
    def increase_speed(self, factor=1.05):
        """Increase ball speed by a factor"""
        self.vx *= factor
        self.vy *= factor
        # Cap max speed to prevent physics breaking
        max_speed = self.original_speed * 2.5
        if abs(self.vx) > max_speed:
            self.vx = max_speed if self.vx > 0 else -max_speed
            
    def reset_speed(self):
        """Reset ball speed to original"""
        self.speed = self.original_speed
        # Maintain direction but reset magnitude
        direction_x = 1 if self.vx > 0 else -1
        direction_y = 1 if self.vy > 0 else -1
        self.vx = self.speed * direction_x
        self.vy = self.speed * direction_y
    
    def update(self, width, height):
        """Update ball position and handle wall collisions"""
        self.x += self.vx
        self.y += self.vy
        
        # Top/bottom wall collision
        if self.y - self.radius <= 0 or self.y + self.radius >= height:
            self.vy = -self.vy
            # Keep ball in bounds
            if self.y - self.radius < 0:
                self.y = self.radius
            if self.y + self.radius > height:
                self.y = height - self.radius
        
        # Check for scoring (left/right boundaries)
        if self.x - self.radius <= 0:
            return 'right_scores'
        if self.x + self.radius >= width:
            return 'left_scores'
        
        return None
    
    def check_paddle_collision(self, paddle):
        """Check and handle paddle collision with spin effect"""
        # Simple AABB collision detection
        if (self.x - self.radius <= paddle.x + paddle.width and
            self.x + self.radius >= paddle.x and
            self.y + self.radius >= paddle.y and
            self.y - self.radius <= paddle.y + paddle.height):
            
            # Reverse horizontal direction
            self.vx = -self.vx
            
            # Add spin based on where ball hits paddle
            paddle_center = paddle.y + paddle.height / 2
            hit_pos = (self.y - paddle_center) / (paddle.height / 2)
            
            # Adjust vertical velocity based on hit position
            self.vy += hit_pos * 2
            
            # Limit vertical velocity
            max_vy = self.speed * 1.5
            if abs(self.vy) > max_vy:
                self.vy = max_vy if self.vy > 0 else -max_vy
            
            # Move ball outside paddle to prevent multiple collisions
            if self.vx > 0:
                self.x = paddle.x + paddle.width + self.radius
            else:
                self.x = paddle.x - self.radius
            
            return True
        
        return False
    
    def reset(self, x, y):
        """Reset ball to center"""
        self.x = x
        self.y = y
        self.vx = -self.vx  # Reverse direction
        self.reset_count += 1

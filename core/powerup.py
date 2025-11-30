"""
Power-Up System
---------------
Handles spawning, collision, and effects of power-ups.
"""
import random
import time
import config
import cv2

# Power-Up Types
TYPE_BIG_PADDLE = 'big_paddle'
TYPE_FAST_BALL = 'fast_ball' # Replaces slow_motion
TYPE_SHRINK_AI = 'shrink_ai'

class PowerUp:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type
        self.radius = 15
        self.active = True
        self.spawn_time = time.time()
        
        # Visuals
        if self.type == TYPE_BIG_PADDLE:
            self.color = (0, 255, 0) # Green
            self.symbol = "+"
        elif self.type == TYPE_FAST_BALL:
            self.color = (255, 0, 255) # Purple
            self.symbol = "F"
        elif self.type == TYPE_SHRINK_AI:
            self.color = (0, 0, 255) # Red
            self.symbol = "-"

class PowerUpManager:
    def __init__(self, game):
        self.game = game
        self.powerups = []
        # active_effects: type -> {'end_time': float, 'stack': int}
        self.active_effects = {} 
        self.last_spawn_time = time.time()
        self.spawn_interval = 5.0 # Seconds (was 10.0)
        
    def update(self, emotion="Neutral"):
        """Update power-ups and spawn new ones"""
        current_time = time.time()
        
        # 1. Spawning Logic
        # Happy players get more power-ups
        interval = self.spawn_interval
        if emotion == "Happy":
            interval = 3.0 # Chaos mode!
        elif emotion == "Frustrated":
            interval = 6.0
            
        if current_time - self.last_spawn_time > interval:
            self._spawn_random_powerup()
            self.last_spawn_time = current_time
            
        # 2. Check Collisions
        ball = self.game.ball
        for pu in self.powerups[:]:
            # Simple Circle Collision
            dist = ((ball.x - pu.x)**2 + (ball.y - pu.y)**2)**0.5
            if dist < (ball.radius + pu.radius):
                self._activate_powerup(pu)
                self.powerups.remove(pu)
                
        # 3. Update Active Effects
        expired_effects = []
        for effect_type, data in self.active_effects.items():
            if current_time > data['end_time']:
                self._deactivate_effect(effect_type)
                expired_effects.append(effect_type)
                
        for effect in expired_effects:
            del self.active_effects[effect]
            
    def _spawn_random_powerup(self):
        """Spawn a power-up in the middle area"""
        margin = 100
        x = random.randint(margin, config.SCREEN_WIDTH - margin)
        y = random.randint(margin, config.SCREEN_HEIGHT - margin)
        
        types = [TYPE_BIG_PADDLE, TYPE_FAST_BALL, TYPE_SHRINK_AI]
        chosen_type = random.choice(types)
        
        self.powerups.append(PowerUp(x, y, chosen_type))
        print(f"Spawned PowerUp: {chosen_type}")
        
    def _activate_powerup(self, powerup):
        """Apply effect with Stacking"""
        duration = 10.0 
        current_time = time.time()
        
        # Check if already active
        if powerup.type in self.active_effects:
            self.active_effects[powerup.type]['stack'] += 1
            self.active_effects[powerup.type]['end_time'] = current_time + duration
            stack = self.active_effects[powerup.type]['stack']
            print(f"PowerUp Stacked! {powerup.type} x{stack}")
        else:
            self.active_effects[powerup.type] = {'end_time': current_time + duration, 'stack': 1}
            stack = 1
            print(f"Activated: {powerup.type}")
            
        # Apply Effect based on Stack
        if powerup.type == TYPE_BIG_PADDLE:
            # Base 80. +70 per stack.
            # x1 = 150, x2 = 220, x3 = 290
            self.game.player_paddle.height = 80 + (70 * stack)
            
        elif powerup.type == TYPE_FAST_BALL:
            # Multiply CURRENT speed, don't reset!
            # This preserves rally momentum.
            self.game.ball.increase_speed(1.5) # 50% boost on top of current speed
            
        elif powerup.type == TYPE_SHRINK_AI:
            # Base 80. Divide by (1 + stack)
            # x1 = 40, x2 = 26, x3 = 20
            self.game.ai_paddle.height = int(80 / (1 + stack))
            
    def _deactivate_effect(self, effect_type):
        """Remove effect"""
        print(f"Effect Ended: {effect_type}")
        if effect_type == TYPE_BIG_PADDLE:
            self.game.player_paddle.height = 80 # Reset
        elif effect_type == TYPE_FAST_BALL:
            # Don't reset speed! Keep the chaos until someone scores.
            # If we reset, it feels like the game suddenly lags.
            pass 
        elif effect_type == TYPE_SHRINK_AI:
            self.game.ai_paddle.height = 80 # Reset

    def draw(self, frame):
        """Draw powerups and active effects"""
        # Draw items on field
        for pu in self.powerups:
            cv2.circle(frame, (int(pu.x), int(pu.y)), pu.radius, pu.color, -1)
            cv2.circle(frame, (int(pu.x), int(pu.y)), pu.radius, (255,255,255), 1)
            cv2.putText(frame, pu.symbol, (int(pu.x)-5, int(pu.y)+5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
                       
        return frame

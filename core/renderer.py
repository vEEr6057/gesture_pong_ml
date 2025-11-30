"""
Renderer for overlaying game on camera feed
"""
import cv2
import config
import time

class GameRenderer:
    def __init__(self):
        self.font_large = cv2.FONT_HERSHEY_SIMPLEX
        self.font_small = cv2.FONT_HERSHEY_SIMPLEX
    
    def render(self, frame, game_state):
        """Render game elements on camera frame"""
        # 1. Draw UI Elements (Background Layer)
        # Draw ELO Rating
        if 'player_rating' in game_state:
            self._draw_elo(frame, game_state['player_rating'])
            
        # Draw Emotion
        if 'emotion' in game_state:
            self._draw_emotion(frame, game_state['emotion'], game_state['frustration'])
            
        # Draw Active Power-Up HUD
        if 'active_effects' in game_state:
            self.draw_active_powerups(frame, game_state['active_effects'])

        # 2. Draw Power-Up Items (Middle Layer)
        if 'powerups' in game_state:
            self._draw_powerup_items(frame, game_state['powerups'])

        # 3. Draw Game Elements (Foreground Layer)
        # Draw center line
        self._draw_center_line(frame, game_state['width'], game_state['height'])
        
        # Draw paddles
        self._draw_paddle(frame, game_state['player_paddle'], config.COLOR_GREEN)
        self._draw_paddle(frame, game_state['ai_paddle'], config.COLOR_RED)
        
        # Draw Ghost Paddle (Prediction)
        if 'predicted_y' in game_state:
            self._draw_ghost_paddle(frame, game_state['player_paddle'].x, game_state['predicted_y'])
        
        # Draw ball (On top of everything!)
        self._draw_ball(frame, game_state['ball'])
        
        # Draw score
        self._draw_score(frame, game_state['player_score'], game_state['ai_score'])
        
        return frame

    def _draw_powerup_items(self, frame, powerups):
        """Draw power-up orbs"""
        for pu in powerups:
            cv2.circle(frame, (int(pu.x), int(pu.y)), pu.radius, pu.color, -1)
            cv2.circle(frame, (int(pu.x), int(pu.y)), pu.radius, (255,255,255), 1)
            cv2.putText(frame, pu.symbol, (int(pu.x)-5, int(pu.y)+5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
    
    def _draw_center_line(self, frame, width, height):
        """Draw dashed center line"""
        line_x = width // 2
        dash_length = 10
        gap_length = 5
        
        y = 0
        while y < height:
            cv2.line(frame, (line_x, y), (line_x, min(y + dash_length, height)), 
                    config.COLOR_WHITE, 2)
            y += dash_length + gap_length
    
    def _draw_paddle(self, frame, paddle, color):
        """Draw paddle rectangle"""
        cv2.rectangle(frame, 
                     (int(paddle.x), int(paddle.y)),
                     (int(paddle.x + paddle.width), int(paddle.y + paddle.height)),
                     color, -1)

    def _draw_ghost_paddle(self, frame, x, y):
        """Draw semi-transparent ghost paddle at predicted position"""
        overlay = frame.copy()
        cv2.rectangle(overlay, 
                     (int(x), int(y)),
                     (int(x + config.PADDLE_WIDTH), int(y + config.PADDLE_HEIGHT)),
                     config.COLOR_CYAN, -1)
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
    
    def _draw_ball(self, frame, ball):
        """Draw ball circle"""
        cv2.circle(frame, (int(ball.x), int(ball.y)), ball.radius, 
                  config.COLOR_WHITE, -1)
    
    def _draw_score(self, frame, player_score, ai_score):
        """Draw score at top center"""
        score_text = f"{player_score}  -  {ai_score}"
        text_size = cv2.getTextSize(score_text, self.font_large, 1, 2)[0]
        text_x = (frame.shape[1] - text_size[0]) // 2
        text_y = 50
        
        cv2.putText(frame, score_text, (text_x, text_y), 
                   self.font_large, 1, config.COLOR_WHITE, 2)

    def _draw_elo(self, frame, rating):
        """Draw player ELO rating with Skill Meter"""
        # Background Bar
        bar_w = 200
        bar_h = 15
        bar_x = config.SCREEN_WIDTH - bar_w - 20 # Bottom Right
        bar_y = config.SCREEN_HEIGHT - 40
        
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (50, 50, 50), -1)
        
        # Progress (Normalize 0-1000 for visual)
        progress = min(max(rating / 1000.0, 0.0), 1.0)
        fill_w = int(bar_w * progress)
        
        # Color gradient based on rating
        color = (0, 255, 255) # Yellow
        if rating > 600: color = (0, 255, 0) # Green
        if rating > 800: color = (255, 0, 255) # Purple
        
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_w, bar_y + bar_h), color, -1)
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (200, 200, 200), 1)
        
        text = f"ELO: {int(rating)}"
        cv2.putText(frame, text, (bar_x, bar_y - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                   
    def _draw_emotion(self, frame, emotion, frustration):
        """Draw procedural emoji"""
        x = 60
        y = config.SCREEN_HEIGHT - 100
        radius = 30
        
        # Face Base
        color = (0, 255, 255) # Yellow
        if emotion == "Frustrated": color = (0, 0, 255) # Red
        if emotion == "Neutral": color = (200, 200, 200) # Grey-ish
        
        cv2.circle(frame, (x, y), radius, color, -1)
        cv2.circle(frame, (x, y), radius, (0, 0, 0), 2)
        
        # Eyes
        eye_color = (0, 0, 0)
        if emotion == "Frustrated":
            # Angry Eyes (Lines)
            cv2.line(frame, (x-15, y-10), (x-5, y-5), eye_color, 2)
            cv2.line(frame, (x+15, y-10), (x+5, y-5), eye_color, 2)
        else:
            # Normal Eyes (Circles)
            cv2.circle(frame, (x-10, y-10), 3, eye_color, -1)
            cv2.circle(frame, (x+10, y-10), 3, eye_color, -1)
            
        # Mouth
        if emotion == "Happy":
            cv2.ellipse(frame, (x, y+5), (15, 10), 0, 0, 180, eye_color, 2)
        elif emotion == "Frustrated":
            cv2.ellipse(frame, (x, y+15), (15, 10), 0, 180, 360, eye_color, 2)
        elif emotion == "Surprised" or emotion == "Poggers":
            cv2.circle(frame, (x, y+10), 8, eye_color, 2)
        else: # Neutral
            cv2.line(frame, (x-10, y+10), (x+10, y+10), eye_color, 2)
            
        # Frustration Bar (Mini)
        bar_w = 60
        bar_h = 5
        bar_x = x - 30
        bar_y = y + 40
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (50,50,50), -1)
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + int(bar_w * frustration), bar_y + bar_h), (0,0,255), -1)

    def draw_active_powerups(self, frame, active_effects):
        """Draw HUD for active powerups"""
        x = config.SCREEN_WIDTH - 150
        y = 100
        
        for effect, data in active_effects.items():
            remaining = int(data['end_time'] - time.time())
            stack = data['stack']
            
            # Icon Background
            cv2.circle(frame, (x, y), 20, (50, 50, 50), -1)
            
            # Symbol
            symbol = "?"
            color = (255, 255, 255)
            if effect == 'big_paddle': 
                symbol = "+"
                color = (0, 255, 0)
            elif effect == 'fast_ball': 
                symbol = "F"
                color = (255, 0, 255)
            elif effect == 'shrink_ai': 
                symbol = "-"
                color = (0, 0, 255)
                
            cv2.putText(frame, symbol, (x-7, y+7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            
            # Text
            text = f"x{stack} ({remaining}s)"
            cv2.putText(frame, text, (x + 30, y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            y += 50

    def draw_fps(self, frame, fps):
        """Draw FPS counter"""
        fps_text = f"FPS: {int(fps)}"
        cv2.putText(frame, fps_text, (10, 30), 
                   self.font_small, 0.6, config.COLOR_YELLOW, 2)
    
    def draw_pause_overlay(self, frame):
        """Draw pause overlay"""
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (frame.shape[1], frame.shape[2]), 
                     (0, 0, 0), -1)
        frame = cv2.addWeighted(frame, 0.7, overlay, 0.3, 0)
        
        pause_text = "PAUSED"
        text_size = cv2.getTextSize(pause_text, self.font_large, 2, 3)[0]
        text_x = (frame.shape[1] - text_size[0]) // 2
        text_y = frame.shape[0] // 2
        
        cv2.putText(frame, pause_text, (text_x, text_y), 
                   self.font_large, 2, config.COLOR_CYAN, 3)
        
        return frame

"""
ML-Enhanced Gesture Pong - Main Entry Point
Week 1: Basic game with hand tracking
"""
import cv2
import time
import sys

from vision.camera import Camera
from vision.hand_tracker import HandTracker
from core.game import PongGame
from core.renderer import GameRenderer
from ml.data_collector import DataCollector
from core.elo_system import EloSystem
from ml.affective_modulator import AffectiveModulator
from ml.emotion_detector import EmotionDetector
from core.powerup import PowerUpManager
import random
import config
from ml.gesture_predictor import GesturePredictor

# We know AI works now, so we can simplify
AI_AVAILABLE = True

class GesturePong:
    def __init__(self):
        self.camera = Camera(width=config.SCREEN_WIDTH, height=config.SCREEN_HEIGHT)
        self.hand_tracker = HandTracker()
        self.game = PongGame()
        self.renderer = GameRenderer()
        self.data_collector = DataCollector()
        self.elo_system = EloSystem()
        self.affective_modulator = AffectiveModulator()
        self.emotion_detector = EmotionDetector()
        self.powerup_manager = PowerUpManager(self.game)
        
        # Apply initial AI parameters
        self._update_ai_difficulty()
        
        if AI_AVAILABLE:
            self.predictor = GesturePredictor()
        else:
            self.predictor = None
        
        self.running = True
        self.fps_counter = FPSCounter()
    
    def run(self):
        """Main game loop"""
        try:
            # Start camera
            self.camera.start()
            
            # Create resizable window
            cv2.namedWindow('ML-Enhanced Gesture Pong', cv2.WINDOW_NORMAL)
            
            print("Starting ML-Enhanced Gesture Pong...")
            print(f"Player Rating: {self.elo_system.player_rating}")
            print("Controls:")
            print("  - Move index finger up/down to control paddle")
            print("  - Press 'P' to pause")
            print("  - Press 'R' to restart")
            print("  - Press 'D' to toggle Data Collection")
            print("  - Press 'Q' to quit")
            
            while self.running:
                # Calculate FPS
                self.fps_counter.update()
                
                # Read camera frame
                frame = self.camera.read_frame()
                if frame is None:
                    print("Failed to read camera frame")
                    break
                
                # Process Hand Tracking (Always runs for paddle control)
                self.hand_tracker.process_frame(frame)
                finger_pos = self.hand_tracker.get_index_finger_position(frame.shape)
                
                # --- GAME LOGIC (Only if NOT paused) ---
                predicted_y = None # Default
                
                if not self.game.is_paused:
                    # 1. Process Emotion
                    emotion, valence, arousal = self.emotion_detector.process_frame(frame)
                    self.affective_modulator.update_emotion(emotion, valence, arousal)
                    
                    # 2. Update Power-Ups
                    self.powerup_manager.update(emotion)
                    
                    # 3. Update Game Physics
                    result = self.game.update()
                    
                    # 4. Record Data
                    self.data_collector.record_frame(self.game.get_state(), finger_pos)
                    
                    # 5. Handle Scoring
                    if result == 'player_won':
                        change = self.elo_system.update_rating(player_won=True)
                        self.affective_modulator.update_outcome(player_won=True)
                        print(f"Player Won! Rating: {int(self.elo_system.player_rating)} (+{int(change)})")
                        self._update_ai_difficulty()
                    elif result == 'ai_won':
                        change = self.elo_system.update_rating(player_won=False)
                        self.affective_modulator.update_outcome(player_won=False)
                        print(f"AI Won! Rating: {int(self.elo_system.player_rating)} ({int(change)})")
                        self._update_ai_difficulty()
                    
                    # 6. TCN Prediction
                    if self.predictor:
                        predicted_y = self.predictor.update_buffer(self.game.get_state(), finger_pos)
                    
                    # 7. Update AI
                    self._update_ai(predicted_y)
                
                else:
                    # If paused, keep previous emotion state for rendering
                    emotion = self.emotion_detector.current_emotion
                
                # --- RENDERING ---
                
                # Update player paddle (Always allow movement even if paused? Or freeze? 
                # User usually wants to move paddle while paused to get ready. 
                # But game update is paused. Let's allow paddle move.)
                if finger_pos:
                    self.game.player_paddle.set_target(finger_pos[1] - self.game.player_paddle.height // 2)

                # Prepare Game State for Renderer
                game_state = self.game.get_state()
                if predicted_y is not None:
                    game_state['predicted_y'] = predicted_y
                    
                game_state['player_rating'] = self.elo_system.player_rating
                game_state['emotion'] = emotion
                game_state['frustration'] = self.affective_modulator.frustration_level
                game_state['powerups'] = self.powerup_manager.powerups
                game_state['active_effects'] = self.powerup_manager.active_effects
                    
                frame = self.renderer.render(frame, game_state)
                
                # Draw hand landmarks
                frame = self.hand_tracker.draw_landmarks(frame)
                frame = self.hand_tracker.draw_finger_indicator(frame, finger_pos)
                
                # Draw FPS
                self.renderer.draw_fps(frame, self.fps_counter.get_fps())
                
                # Draw Recording Status
                if self.data_collector.is_recording:
                    cv2.circle(frame, (30, 60), 10, (0, 0, 255), -1) # Red dot
                    cv2.putText(frame, f"REC {len(self.data_collector.data_buffer)}", (50, 65), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # Draw pause overlay if paused
                if self.game.is_paused:
                    frame = self.renderer.draw_pause_overlay(frame)
                
                # Display frame
                cv2.imshow('ML-Enhanced Gesture Pong', frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    self.running = False
                elif key == ord('p'):
                    self.game.pause()
                elif key == ord('r'):
                    self.game.restart()
                elif key == ord('d'):
                    if self.data_collector.is_recording:
                        self.data_collector.stop_recording()
                    else:
                        self.data_collector.start_recording()
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.data_collector.stop_recording()
            if self.predictor:
                self.predictor.stop()
            self.cleanup()
    
    def _update_ai_difficulty(self):
        """Update AI parameters based on ELO and Affective State"""
        params = self.elo_system.get_ai_parameters()
        modifier = self.affective_modulator.get_difficulty_modifier()
        
        # Apply Pity Mode Modifier
        if modifier < 1.0:
            params['speed'] *= modifier
            params['error_margin'] /= modifier 
            
        self.game.set_ai_parameters(params)

    def _update_ai(self, predicted_player_y=None):
        """
        Advanced AI:
        1. Tracks ball (Basic)
        2. Uses TCN Prediction to aim away from player (Advanced)
        3. Applies ELO error (Human-like)
        """
        ball = self.game.ball
        ai_paddle = self.game.ai_paddle
        player_paddle = self.game.player_paddle
        
        # 1. Basic Target: The Ball
        target_y = ball.y - ai_paddle.height // 2
        
        # 2. Advanced Strategy: Aim away from player
        # Only apply strategy if ball is moving towards AI and we have a prediction
        if ball.vx > 0 and predicted_player_y is not None:
            # If player is going UP (low Y), aim DOWN (add offset)
            # If player is going DOWN (high Y), aim UP (subtract offset)
            
            # Center of screen
            center_y = config.SCREEN_HEIGHT / 2
            
            # If player is predicted to be in top half, try to hit to bottom half
            if predicted_player_y < center_y:
                strategic_offset = 30 # Aim lower
            else:
                strategic_offset = -30 # Aim higher
                
            # Blend strategy with basic tracking (30% strategy, 70% tracking)
            target_y += strategic_offset
            
        # 3. Apply ELO Error (Human-like imperfection)
        # BUG FIX: Apply error ALWAYS, not just when far away.
        # Otherwise AI snaps to perfection at the last second.
        error_offset = (random.random() - 0.5) * 2 * self.game.ai_error_margin
        target_y += error_offset
            
        # Move AI
        if ball.vx > 0:
            ai_paddle.set_target(target_y)
        else:
            # Return to center when idle
            center_y = self.game.height // 2 - ai_paddle.height // 2
            ai_paddle.set_target(center_y)
    
    def cleanup(self):
        """Cleanup resources"""
        print("\nCleaning up...")
        self.camera.release()
        self.hand_tracker.cleanup()
        cv2.destroyAllWindows()
        print("Goodbye!")


class FPSCounter:
    """Simple FPS counter"""
    def __init__(self, buffer_size=30):
        self.buffer_size = buffer_size
        self.frame_times = []
        self.last_time = time.time()
    
    def update(self):
        """Update FPS calculation"""
        current_time = time.time()
        frame_time = current_time - self.last_time
        self.last_time = current_time
        
        self.frame_times.append(frame_time)
        if len(self.frame_times) > self.buffer_size:
            self.frame_times.pop(0)
    
    def get_fps(self):
        """Get current FPS"""
        if not self.frame_times:
            return 0
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        return 1.0 / avg_frame_time if avg_frame_time > 0 else 0


if __name__ == "__main__":
    game = GesturePong()
    game.run()

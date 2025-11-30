"""
Data Collection Module for ML Training
Records gameplay state (ball, paddles, finger) for TCN training
"""
import time
import pandas as pd
import os
import config

class DataCollector:
    def __init__(self):
        self.data_buffer = []
        self.is_recording = False
        self.session_id = int(time.time())
        self.frame_count = 0
        
        # Ensure data directory exists
        os.makedirs(config.GAMEPLAY_SESSIONS_DIR, exist_ok=True)
        
    def start_recording(self):
        """Start recording data"""
        self.is_recording = True
        self.data_buffer = []
        self.session_id = int(time.time())
        print(f"Started recording session {self.session_id}")
        
    def stop_recording(self):
        """Stop recording and save data"""
        self.is_recording = False
        if self.data_buffer:
            # FIX: Always append on stop, otherwise we overwrite the whole file with the last few frames!
            self.save_data(append=True)
            
    def record_frame(self, game_state, finger_pos):
        """Record a single frame of data"""
        if not self.is_recording:
            return
            
        # Extract data
        player_paddle = game_state['player_paddle']
        ball = game_state['ball']
        
        frame_data = {
            'timestamp': time.time(),
            'session_id': self.session_id,
            'frame_id': self.frame_count,
            
            # Player Paddle (Target for ML)
            'player_y': player_paddle.y,
            'player_velocity': player_paddle.get_velocity(),
            
            # Ball State (Input for ML)
            'ball_x': ball.x,
            'ball_y': ball.y,
            'ball_vx': ball.vx,
            'ball_vy': ball.vy,
            
            # Finger Input (Input for ML)
            'finger_y': finger_pos[1] if finger_pos else -1,
            
            # Game Context
            'rally_length': game_state['current_rally_length']
        }
        
        self.data_buffer.append(frame_data)
        self.frame_count += 1
        
        # Auto-save every 1000 frames to prevent data loss
        if len(self.data_buffer) >= 1000:
            self.save_data(append=True)
            self.data_buffer = []
            
    def save_data(self, append=False):
        """Save buffer to CSV"""
        if not self.data_buffer:
            return
            
        df = pd.DataFrame(self.data_buffer)
        filename = os.path.join(config.GAMEPLAY_SESSIONS_DIR, f"session_{self.session_id}.csv")
        
        if append and os.path.exists(filename):
            df.to_csv(filename, mode='a', header=False, index=False)
        else:
            df.to_csv(filename, index=False)
            
        print(f"Saved {len(self.data_buffer)} frames to {filename}")

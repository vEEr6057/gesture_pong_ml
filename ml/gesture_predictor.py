"""
Gesture Predictor Module
Loads trained TCN model and predicts future finger position
"""
import tensorflow as tf
from tensorflow import keras
import numpy as np
import config
import os

from ml.tcn_model import build_tcn_model

import threading
import queue

class GesturePredictor:
    def __init__(self, model_path="models/tcn_gesture_model.h5"):
        self.model = None
        self.sequence_buffer = []
        self.sequence_length = config.LSTM_SEQUENCE_LENGTH # 30 frames
        self.is_ready = False
        self.latest_prediction = None
        self.running = True
        
        # Queue for passing input sequences to the worker thread
        self.input_queue = queue.Queue(maxsize=1)
        
        try:
            if os.path.exists(model_path):
                print(f"Loading TCN model from {model_path}...")
                
                # STRATEGY CHANGE: Build architecture locally, then load weights.
                input_shape = (self.sequence_length, 6) # 6 features
                self.model = build_tcn_model(input_shape)
                self.model.load_weights(model_path)
                
                self.is_ready = True
                print("TCN Model loaded successfully! (Async Mode)")
                
                # Start background worker thread
                self.worker_thread = threading.Thread(target=self._prediction_worker, daemon=True)
                self.worker_thread.start()
                
            else:
                print(f"Warning: Model not found at {model_path}")
        except Exception as e:
            print(f"Error loading model: {e}")
            
    def _prediction_worker(self):
        """Background thread that runs the heavy model inference"""
        while self.running:
            try:
                # Wait for new input (blocking)
                input_seq = self.input_queue.get(timeout=0.1)
                
                # Run inference
                prediction = self.model(input_seq, training=False)
                
                # Update latest prediction
                self.latest_prediction = float(prediction[0][0]) * config.SCREEN_HEIGHT
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Prediction thread error: {e}")

    def update_buffer(self, game_state, finger_pos):
        """Add current frame to buffer and return latest prediction (non-blocking)"""
        if not self.is_ready:
            return None
            
        # Extract features
        player_paddle = game_state['player_paddle']
        ball = game_state['ball']
        
        features = [
            ball.x / config.SCREEN_WIDTH,
            ball.y / config.SCREEN_HEIGHT,
            ball.vx / 20.0,
            ball.vy / 20.0,
            player_paddle.y / config.SCREEN_HEIGHT,
            (finger_pos[1] if finger_pos else 0) / config.SCREEN_HEIGHT
        ]
        
        self.sequence_buffer.append(features)
        
        if len(self.sequence_buffer) > self.sequence_length:
            self.sequence_buffer.pop(0)
            
        # If buffer is full, try to send to worker
        if len(self.sequence_buffer) == self.sequence_length:
            # Only send if worker is ready (queue empty) to avoid backlog
            if self.input_queue.empty():
                input_seq = np.array([self.sequence_buffer])
                self.input_queue.put(input_seq)
            
        return self.latest_prediction
        
    def stop(self):
        self.running = False

"""
Emotion Detector using MediaPipe Face Mesh
------------------------------------------
Detects basic emotional states (Happy, Frustrated, Neutral) using geometric features.
Replaces heavy CNN models for real-time performance.
"""
import cv2
import mediapipe as mp
import math

import collections

class EmotionDetector:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Emotion State
        self.current_emotion = "Neutral"
        self.arousal_level = 0.0 # 0.0 (Calm) to 1.0 (Excited/Stressed)
        self.valence = 0.0       # -1.0 (Negative) to 1.0 (Positive)
        
        # Smoothing Buffers (Moving Average)
        self.buffer_size = 10
        self.smile_buffer = collections.deque(maxlen=self.buffer_size)
        self.open_buffer = collections.deque(maxlen=self.buffer_size)
        self.brow_buffer = collections.deque(maxlen=self.buffer_size)
        
        # Debug Values
        self.debug_smile = 0.0
        self.debug_open = 0.0
        self.debug_brow = 0.0
        
    def process_frame(self, frame):
        """
        Process frame and estimate emotion.
        Returns: (emotion_label, valence, arousal)
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0]
            self._analyze_landmarks(landmarks, frame.shape)
            return self.current_emotion, self.valence, self.arousal_level
            
        return None, 0.0, 0.0
        
    def _analyze_landmarks(self, landmarks, shape):
        """Calculate geometric features for emotion"""
        h, w, _ = shape
        
        # Helper to get coords
        def get_pt(idx):
            return (landmarks.landmark[idx].x * w, landmarks.landmark[idx].y * h)
            
        # 1. Smile Detection (Mouth Width vs Face Width)
        # We normalize mouth width by jaw width to account for distance
        mouth_left = get_pt(61)
        mouth_right = get_pt(291)
        jaw_left = get_pt(234)
        jaw_right = get_pt(454)
        
        mouth_width = math.dist(mouth_left, mouth_right)
        face_width = math.dist(jaw_left, jaw_right)
        
        smile_ratio = mouth_width / face_width
        self.smile_buffer.append(smile_ratio)
        
        # 2. Mouth Open (Surprise/Stress)
        lip_top = get_pt(13)
        lip_bottom = get_pt(14)
        mouth_height = math.dist(lip_top, lip_bottom)
        open_ratio = mouth_height / mouth_width
        self.open_buffer.append(open_ratio)
        
        # 3. Brow Furrow (Anger/Focus) - Distance between inner brows
        brow_left = get_pt(55)
        brow_right = get_pt(285)
        brow_dist = math.dist(brow_left, brow_right)
        brow_ratio = brow_dist / face_width
        self.brow_buffer.append(brow_ratio)
        
        # --- Smoothed Values ---
        avg_smile = sum(self.smile_buffer) / len(self.smile_buffer)
        avg_open = sum(self.open_buffer) / len(self.open_buffer)
        avg_brow = sum(self.brow_buffer) / len(self.brow_buffer)
        
        self.debug_smile = avg_smile
        self.debug_open = avg_open
        self.debug_brow = avg_brow
        
        # --- Logic ---
        
        # Smile Thresholds (Re-tuned)
        # Was 0.38 (too sensitive), now 0.42
        if avg_smile > 0.42: 
            self.current_emotion = "Happy"
            self.valence = 0.8
        elif avg_smile < 0.32: # Narrow mouth
            self.current_emotion = "Focused"
            self.valence = 0.1
        else:
            self.current_emotion = "Neutral"
            self.valence = 0.0
            
        # Mouth Open Override
        if avg_open > 0.3:
            self.current_emotion = "Surprised"
            self.arousal_level = 0.8
        elif avg_open > 0.5:
            self.current_emotion = "Poggers"
            self.arousal_level = 1.0
        else:
            self.arousal_level = 0.2
            
        # Brow Override (Anger/Frustration)
        # Was < 0.23 (too sensitive), now < 0.20
        if avg_brow < 0.20 and self.valence < 0.5:
            self.current_emotion = "Frustrated"
            self.valence = -0.6
            self.arousal_level = 0.7

    def draw_mesh(self, frame):
        """Debug: Draw face mesh and stats"""
        # Draw stats
        y = 150
        cv2.putText(frame, f"Smile: {self.debug_smile:.2f}", (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.putText(frame, f"Open: {self.debug_open:.2f}", (20, y+20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.putText(frame, f"Brow: {self.debug_brow:.2f}", (20, y+40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        return frame

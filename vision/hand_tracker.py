"""
MediaPipe hand tracking wrapper
"""
import mediapipe as mp
import cv2

class HandTracker:
    def __init__(self, max_hands=1, detection_confidence=0.8, tracking_confidence=0.5):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.results = None
    
    def process_frame(self, frame):
        """Process frame and detect hands"""
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(rgb_frame)
        return self.results
    
    def get_index_finger_position(self, frame_shape):
        """Extract index finger tip position (landmark 8)"""
        if not self.results or not self.results.multi_hand_landmarks:
            return None
        
        # Get first detected hand
        hand_landmarks = self.results.multi_hand_landmarks[0]
        index_tip = hand_landmarks.landmark[8]  # Index finger tip
        
        h, w, _ = frame_shape
        x = int(index_tip.x * w)
        y = int(index_tip.y * h)
        
        return (x, y)
    
    def get_all_landmarks(self, frame_shape):
        """Get all 21 landmarks for first detected hand"""
        if not self.results or not self.results.multi_hand_landmarks:
            return None
        
        hand_landmarks = self.results.multi_hand_landmarks[0]
        h, w, _ = frame_shape
        
        landmarks = []
        for landmark in hand_landmarks.landmark:
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            z = landmark.z
            landmarks.append((x, y, z))
        
        return landmarks
    
    def draw_landmarks(self, frame):
        """Draw hand landmarks on frame"""
        if self.results and self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame, 
                    hand_landmarks, 
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    self.mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2)
                )
        
        return frame
    
    def draw_finger_indicator(self, frame, finger_pos):
        """Draw circle at finger position"""
        if finger_pos:
            cv2.circle(frame, finger_pos, 10, (0, 255, 0), -1)
            cv2.circle(frame, finger_pos, 12, (255, 255, 255), 2)
        
        return frame
    
    def cleanup(self):
        """Release MediaPipe resources"""
        if self.hands:
            self.hands.close()

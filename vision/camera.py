"""
Camera capture and management
"""
import cv2

class Camera:
    def __init__(self, camera_index=0, width=800, height=600):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.cap = None
        self.is_open = False
    
    def start(self):
        """Initialize and start camera"""
        self.cap = cv2.VideoCapture(self.camera_index)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open camera {self.camera_index}")
        
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        self.is_open = True
        print(f"Camera {self.camera_index} started: {self.width}x{self.height}")
    
    def read_frame(self):
        """Read a frame from camera"""
        if not self.is_open:
            return None
        
        ret, frame = self.cap.read()
        
        if not ret:
            print("Failed to read frame from camera")
            return None
        
        # Resize frame to match configured dimensions
        if frame.shape[1] != self.width or frame.shape[0] != self.height:
            frame = cv2.resize(frame, (self.width, self.height))
            
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        return frame
    
    def release(self):
        """Release camera resources"""
        if self.cap is not None:
            self.cap.release()
            self.is_open = False
            print("Camera released")
    
    def __del__(self):
        """Cleanup on deletion"""
        self.release()

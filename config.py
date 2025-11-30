# Configuration constants for ML-Enhanced Gesture Pong

# Display settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS_TARGET = 30

# Game settings
BALL_RADIUS = 10
BALL_SPEED = 5
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 80
PADDLE_SPEED = 5

# ML settings
LSTM_SEQUENCE_LENGTH = 30  # 1 second at 30 FPS
LSTM_PREDICTION_HORIZON = 10  # 0.33 seconds ahead
EMOTION_DETECTION_INTERVAL = 3  # Detect emotion every 3rd frame (10 FPS)
EMOTION_ACCURACY_TARGET = 0.95  # 95% accuracy before stopping data collection

# Adaptive difficulty settings
DIFFICULTY_WINDOW_SIZE = 100  # Frames to consider for skill assessment
TARGET_WIN_RATE = 0.55  # Target 55% player win rate
ADJUSTMENT_RATE = 0.05  # How fast difficulty adapts

# Power-up settings
POWERUP_SPAWN_MIN = 10  # Minimum seconds between spawns
POWERUP_SPAWN_MAX = 30  # Maximum seconds between spawns
POWERUP_DURATION_MIN = 6  # Minimum duration in seconds
POWERUP_DURATION_MAX = 15  # Maximum duration in seconds

# Colors (BGR format for OpenCV)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_RED = (0, 0, 255)
COLOR_BLUE = (255, 0, 0)
COLOR_YELLOW = (0, 255, 255)
COLOR_CYAN = (255, 255, 0)
COLOR_MAGENTA = (255, 0, 255)

# Paths
DATA_DIR = "data"
MODELS_DIR = "models"
GAMEPLAY_SESSIONS_DIR = "data/gameplay_sessions"
PLAYER_METRICS_DIR = "data/player_metrics"
EMOTION_DATA_DIR = "data/emotion_data"

"""
TCN Training Script for Google Colab
------------------------------------
INSTRUCTIONS:
1. Go to https://colab.research.google.com/
2. Create a new notebook.
3. Upload your 'session_XXXX.csv' file from 'data/gameplay_sessions/' to the Colab files area.
4. Copy and paste the code below into a code cell and run it.
5. Download the trained 'tcn_gesture_model.h5' file.
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, models
import matplotlib.pyplot as plt
import glob
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
SEQUENCE_LENGTH = 30   # Input: Last 30 frames (1 second)
PREDICTION_HORIZON = 5 # Output: Predict 5 frames ahead (~160ms)
BATCH_SIZE = 32
EPOCHS = 50

# Features to use for prediction
# We use ball state + current paddle/finger state to predict future finger position
FEATURE_COLS = ['ball_x', 'ball_y', 'ball_vx', 'ball_vy', 'player_y', 'finger_y']
TARGET_COL = 'finger_y' 

# ==========================================
# 2. DATA LOADING & PREPROCESSING
# ==========================================
def load_data():
    print("Loading data...")
    csv_files = glob.glob("*.csv")
    
    if not csv_files:
        print("❌ ERROR: No CSV files found!")
        print("Please upload your 'session_X.csv' files to the Colab file browser.")
        return None
        
    df_list = []
    for f in csv_files:
        print(f"Loading {f}...")
        df = pd.read_csv(f)
        df_list.append(df)
    
    full_df = pd.concat(df_list, ignore_index=True)
    print(f"✅ Loaded {len(full_df)} total frames.")
    return full_df

def create_sequences(df):
    data = df[FEATURE_COLS].values
    targets = df[TARGET_COL].values
    
    # Normalize data (Simple MinMax scaling for screen coordinates)
    # Assuming 800x600 screen. Velocity is relative.
    # Ideally we'd fit a scaler, but hardcoding is safer for the game inference later
    data[:, 0] /= 800.0 # ball_x
    data[:, 1] /= 600.0 # ball_y
    data[:, 2] /= 20.0  # ball_vx (approx max speed)
    data[:, 3] /= 20.0  # ball_vy
    data[:, 4] /= 600.0 # player_y
    data[:, 5] /= 600.0 # finger_y
    
    targets = targets / 600.0 # Normalize target too
    
    X = []
    y = []
    
    # Create sliding windows
    for i in range(len(data) - SEQUENCE_LENGTH - PREDICTION_HORIZON):
        # Input: Frames i to i+30
        X.append(data[i : i + SEQUENCE_LENGTH])
        
        # Target: Frame i+30+5 (Future position)
        y.append(targets[i + SEQUENCE_LENGTH + PREDICTION_HORIZON])
        
    return np.array(X), np.array(y)

# ==========================================
# 3. TCN MODEL ARCHITECTURE
# ==========================================
def build_tcn_model(input_shape):
    inputs = layers.Input(shape=input_shape)
    
    # Block 1: Dilation 1
    x = layers.Conv1D(64, 3, dilation_rate=1, padding='causal', activation='relu')(inputs)
    x = layers.Dropout(0.1)(x)
    
    # Block 2: Dilation 2
    x = layers.Conv1D(64, 3, dilation_rate=2, padding='causal', activation='relu')(x)
    x = layers.Dropout(0.1)(x)
    
    # Block 3: Dilation 4
    x = layers.Conv1D(64, 3, dilation_rate=4, padding='causal', activation='relu')(x)
    x = layers.Dropout(0.1)(x)
    
    # Block 4: Dilation 8 (Receptive field covers sequence)
    x = layers.Conv1D(64, 3, dilation_rate=8, padding='causal', activation='relu')(x)
    x = layers.Dropout(0.1)(x)
    
    x = layers.GlobalAveragePooling1D()(x)
    outputs = layers.Dense(1, activation='linear')(x)
    
    model = models.Model(inputs, outputs, name="GestureTCN")
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    return model

# ==========================================
# 4. MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    # 1. Load
    df = load_data()
    
    if df is not None:
        # 2. Process
        print("Creating sequences...")
        X, y = create_sequences(df)
        print(f"Training Data Shape: {X.shape}")
        print(f"Target Data Shape: {y.shape}")
        
        # 3. Build
        print("Building TCN Model...")
        model = build_tcn_model(input_shape=(SEQUENCE_LENGTH, len(FEATURE_COLS)))
        model.summary()
        
        # 4. Train
        print("Starting Training...")
        history = model.fit(
            X, y,
            epochs=EPOCHS,
            batch_size=BATCH_SIZE,
            validation_split=0.2,
            verbose=1
        )
        
        # 5. Save
        print("Saving model...")
        model.save('tcn_gesture_model.h5')
        print("✅ Model saved as 'tcn_gesture_model.h5'")
        
        # 6. Plot
        plt.plot(history.history['loss'], label='Train Loss')
        plt.plot(history.history['val_loss'], label='Val Loss')
        plt.legend()
        plt.title('TCN Training Progress')
        plt.show()

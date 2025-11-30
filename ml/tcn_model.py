"""
Temporal Convolutional Network (TCN) for Gesture Prediction
Architecture: Causal Dilated Convolutions for low-latency time-series prediction
"""
import tensorflow as tf
from tensorflow.keras import layers, models

def build_tcn_model(input_shape, output_units=1):
    """
    Builds a TCN model for gesture prediction.
    
    Args:
        input_shape: (sequence_length, features)
        output_units: Number of values to predict (1 for paddle Y)
        
    Returns:
        Compiled Keras model
    """
    inputs = layers.Input(shape=input_shape)
    
    # Block 1: Dilation 1 (Receptive field: 3)
    x = layers.Conv1D(filters=64, kernel_size=3, dilation_rate=1, padding='causal', activation='relu')(inputs)
    x = layers.Dropout(0.1)(x)
    
    # Block 2: Dilation 2 (Receptive field: 7)
    x = layers.Conv1D(filters=64, kernel_size=3, dilation_rate=2, padding='causal', activation='relu')(x)
    x = layers.Dropout(0.1)(x)
    
    # Block 3: Dilation 4 (Receptive field: 15)
    x = layers.Conv1D(filters=64, kernel_size=3, dilation_rate=4, padding='causal', activation='relu')(x)
    x = layers.Dropout(0.1)(x)
    
    # Block 4: Dilation 8 (Receptive field: 31) - Covers full 30-frame sequence
    x = layers.Conv1D(filters=64, kernel_size=3, dilation_rate=8, padding='causal', activation='relu')(x)
    x = layers.Dropout(0.1)(x)
    
    # Global Average Pooling to flatten sequence
    x = layers.GlobalAveragePooling1D()(x)
    
    # Output layer
    outputs = layers.Dense(output_units, activation='linear')(x)
    
    model = models.Model(inputs=inputs, outputs=outputs, name="GestureTCN")
    
    model.compile(
        optimizer='adam',
        loss='mse',
        metrics=['mae']
    )
    
    return model

if __name__ == "__main__":
    # Test model build
    model = build_tcn_model(input_shape=(30, 6)) # 30 frames, 6 features (ball x,y,vx,vy, paddle y, finger y)
    model.summary()

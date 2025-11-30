# 🏓 ML-Based Gesture Pong

> **A Trimodal Adaptive Game Design Prototype**  
> *Powered by Computer Vision, TCNs, and Affective Computing*

## Overview
**ML-Enhanced Gesture Pong** is not just a game; it is a research prototype demonstrating **Trimodal Adaptive Game Design (TAGD)**. Unlike traditional games with static difficulty, this system builds a holistic model of the player in real-time using three data streams:

1.  **Kinetic (Gesture):** Ultra-low latency hand tracking using a **Temporal Convolutional Network (TCN)** for predictive control.
2.  **Cognitive (Skill):** An **ELO-based** difficulty system that adapts to your win/loss ratio.
3.  **Affective (Emotion):** Real-time **Facial Emotion Recognition** that adjusts game dynamics based on your mood (e.g., frustration, happiness).

---

## Key Features

### Advanced AI Opponent
*   **TCN Prediction:** The AI uses a trained Deep Learning model (TCN) to predict *your* future paddle position based on your hand movement trajectory.
*   **Human-Like Error:** The AI isn't perfect; it makes calculated mistakes based on its ELO rating, simulating a human opponent.

### Affective Computing
*   **Emotion Detection:** Uses MediaPipe Face Mesh to detect smiles, frowns, and surprise in real-time.
*   **Adaptive Gameplay:**
    *   **Frustrated?** The game might spawn helpful power-ups or slightly lower the difficulty.
    *   **Happy?** The game enters "Chaos Mode" with faster power-up spawns!
    *   **Bored?** The AI becomes more aggressive.

### Procedural Power-Ups
Dynamic power-ups spawn based on the game state:
*   **Big Paddle:** Increases your paddle size.
*   **Fast Ball:** Multiplies ball speed (stacks for insane velocity!).
*   **Shrink AI:** Reduces the AI paddle size.
*   *Stacking Mechanics:* Collecting the same power-up multiple times amplifies its effect (e.g., 2x, 3x speed).

---

## Installation

### Prerequisites
*   Python 3.9 or higher
*   Webcam

### Setup
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/gesture-pong-ml.git
    cd gesture-pong-ml
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

---

## How to Play

1.  **Run the game:**
    ```bash
    python main.py
    ```

2.  **Controls:**
    *   **👆 Index Finger:** Move your index finger UP or DOWN to control the paddle.
    *   **⏸️ 'P':** Pause Game.
    *   **🔄 'R':** Restart Game.
    *   **📹 'D':** Toggle Data Collection (for retraining).
    *   **❌ 'Q':** Quit.

3.  **HUD Guide:**
    *   **Bottom Left:** Your current Emotion (Emoji) and Frustration Level.
    *   **Bottom Right:** Your Skill Meter (ELO Rating).
    *   **Right Side:** Active Power-Ups and timers.

---

## Project Structure

*   `core/`: Game physics, paddle logic, and rendering engine.
*   `vision/`: Camera handling and MediaPipe hand tracking.
*   `ml/`: Machine Learning modules.
    *   `tcn_model.py`: Architecture of the Temporal Convolutional Network.
    *   `emotion_detector.py`: Geometric facial feature analysis.
    *   `affective_modulator.py`: Logic for adjusting difficulty based on emotion.
*   `data/`: Gameplay session recordings (CSVs).

---

## Technical Details

### The TCN Model
We chose a **Temporal Convolutional Network** over LSTMs for gesture prediction due to its superior parallelization and lower inference latency (< 5ms). The model takes a sequence of 30 frames (ball physics + hand position) and predicts the player's intent 5 frames into the future.

### ELO System
The difficulty is not linear. It uses a modified **ELO rating system** (starting at 1200).
*   **Win:** Rating increases, AI becomes faster and more precise.
*   **Loss:** Rating decreases, AI becomes slower and more forgiving.

---

## License
This project is open-source and available under the MIT License.

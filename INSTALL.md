# Installation Guide - ML-Enhanced Gesture Pong

## ⚠️ IMPORTANT: Python Version Requirement

**MediaPipe requires Python 3.9, 3.10, or 3.11**
- ❌ Python 3.13+ is NOT supported
- ✅ Python 3.11.x is recommended

## Check Your Python Version
```bash
python --version
```

If you have Python 3.13+, you need to install Python 3.11:
- Download from: https://www.python.org/downloads/
- Install Python 3.11.x
- Make sure to check "Add Python to PATH"

## Installation Steps

### 1. Create Virtual Environment with Python 3.11
```bash
# If you have multiple Python versions, specify Python 3.11
py -3.11 -m venv venv

# Or if Python 3.11 is your default
python -m venv venv
```

### 2. Activate Virtual Environment
```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Upgrade pip
```bash
python -m pip install --upgrade pip
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

This will install:
- opencv-python (camera & rendering)
- mediapipe (hand tracking)
- tensorflow (LSTM & emotion models)
- scikit-learn (data processing)
- pandas (data handling)
- matplotlib (visualization)
- numpy (numerical operations)
- joblib (model persistence)

### 5. Verify Installation
```bash
python -c "import cv2, mediapipe, tensorflow; print('All dependencies installed successfully!')"
```

## Run the Game
```bash
python main.py
```

## Troubleshooting

### MediaPipe Installation Fails
- **Cause**: Wrong Python version (3.13+)
- **Solution**: Use Python 3.9-3.11

### Camera Not Found
- **Cause**: No webcam or wrong camera index
- **Solution**: Check camera in Device Manager (Windows) or System Preferences (Mac)

### Low FPS (<20)
- **Cause**: Weak CPU or high resolution
- **Solution**: Reduce camera resolution in `config.py`

### Import Errors
- **Cause**: Virtual environment not activated
- **Solution**: Run `venv\Scripts\activate` first

## Next Steps

After successful installation:
1. Play the game to test hand tracking
2. Week 2: Start data collection for LSTM training
3. Week 3: Train LSTM model on Google Colab

## Need Help?
- Check Python version: `python --version`
- Check installed packages: `pip list`
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

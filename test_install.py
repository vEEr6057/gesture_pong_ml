# Quick Installation Test Script
import sys
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")

try:
    import pip
    print(f"Pip version: {pip.__version__}")
except:
    print("Pip not found")

# Try installing a simple package
import subprocess
result = subprocess.run([sys.executable, "-m", "pip", "install", "--dry-run", "requests"], 
                       capture_output=True, text=True)
print("\nDry run test:")
print(result.stdout)
print(result.stderr)

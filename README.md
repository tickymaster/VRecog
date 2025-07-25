# VRecog - Real-time Vowel Recognition System

A complete real-time formant detection and vowel recognition system using C++ for performance and Python for machine learning and user interface.

## Quick Start

```bash
# 1. Install system dependencies (Ubuntu/Debian)
sudo apt-get install python3-dev cmake build-essential libfftw3-dev portaudio19-dev pkg-config

# 2. Set up the project
cd /path/to/v_project
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# 3. Run the vowel recognition program
.venv/bin/python app/classification.py
```

## Features

- Real-time audio processing using PortAudio
- FFT-based spectral analysis with FFTW3
- Gaussian smoothing and peak detection
- Formant frequency extraction (F1, F2)
- Python bindings via pybind11
- Machine learning vowel classification with scikit-learn
- Interactive training and testing interface
- Audio device management
- Training data persistence

## Prerequisites

Before installation, make sure you have the required system dependencies:

### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y \
    python3-dev \
    python3-pip \
    cmake \
    build-essential \
    libfftw3-dev \
    portaudio19-dev \
    pkg-config
```

### macOS:
```bash
brew install fftw portaudio cmake pkg-config
```

## Installation

### Step 1: Set up Virtual Environment
```bash
# Clone or navigate to the project directory
cd /path/to/v_project

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate
```

### Step 2: Install the Project
For development and testing, use editable installation:

```bash
# Install in editable mode (with virtual environment activated)
pip install -e .
```

### Alternative: Direct Installation
For production use:

```bash
# Install normally
pip install .
```

### Step 3: Run the Program
```bash
# Option 1: Direct path to virtual environment python
.venv/bin/python app/classification.py

# Option 2: With activated virtual environment
source .venv/bin/activate
python app/classification.py
```

## Usage

### Running the Vowel Recognition Program

To run the complete vowel recognition and training program:

```bash
# Make sure you're in the project directory
cd /home/tony/projects/c++/v_project

# Activate the virtual environment and run the program
.venv/bin/python app/classification.py
```

Or if you have the virtual environment activated:

```bash
# First activate the virtual environment
source .venv/bin/activate

# Then run the program
python app/classification.py
```

This will launch the interactive vowel recognition training program with options to:
- Train vowel sounds (A, E, I, O, U)
- Test real-time vowel recognition
- Manage audio devices
- Save/load training data
- Test model accuracy

### Basic Library Usage

```python
import formant_detector

# Create detector instance
detector = formant_detector.FormantDetector()

# List available audio devices
detector.print_devices()

# Start real-time detection (use appropriate device ID)
detector.start_stream(deviceInput=4)

# Get current formant frequencies
formants = detector.get_formants()
print(f"F1: {formants[0]} Hz, F2: {formants[1]} Hz")

# Stop detection
detector.stop_stream()
```

### Real-time Monitoring Example

```python
import formant_detector
import time

detector = formant_detector.FormantDetector()

try:
    # Start detection
    detector.start_stream()
    print("Listening for formants... (Press Ctrl+C to stop)")
    
    # Monitor for 10 seconds
    for i in range(100):
        formants = detector.get_formants()
        if formants[0] > 0 and formants[1] > 0:  # Valid formants detected
            print(f"F1: {formants[0]:.0f} Hz, F2: {formants[1]:.0f} Hz")
        time.sleep(0.1)
        
finally:
    detector.stop_stream()
```

## Testing

Run the test script to verify installation:

```bash
python test/test_formant.py
```

## API Reference

### FormantDetector Class

- `FormantDetector()` - Constructor
- `start_stream(deviceInput=4)` - Start audio capture and processing
- `stop_stream()` - Stop audio processing
- `get_formants()` - Returns list `[F1, F2]` of detected formant frequencies
- `print_devices()` - List available audio input devices

## Configuration

The detector uses these default parameters:
- Sample Rate: 44,100 Hz
- Buffer Size: 4,096 samples
- Frequency Range: 300-3,200 Hz (speech formants)
- Smoothing: Gaussian kernel with σ=0.5

## Troubleshooting

### Import Error
If you get `ImportError: No module named 'formant_detector'`:
1. Make sure you installed the module: `pip install -e .`
2. Check that you're using the correct Python environment

### Audio Device Issues
If audio capture fails:
1. Run `detector.print_devices()` to see available devices
2. Use the correct device ID in `start_stream(deviceInput=ID)`
3. Ensure your microphone has permissions (macOS/Linux)

### Build Errors
If compilation fails:
1. Ensure all system dependencies are installed
2. Check that CMake version is 3.12 or higher: `cmake --version`
3. Try cleaning and rebuilding: `rm -rf build/` then `pip install -e .`

## License

MIT License - see [LICENSE](LICENSE) file for details.

Copyright (c) 2025 tickymaster

This project is provided "as is" without warranty of any kind. See the LICENSE file for full terms.

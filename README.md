# Motion Detection Camera

A Python application that detects movement via webcam and automatically records video when motion is detected.

## Features

- Real-time motion detection using frame differencing
- Automatic recording when movement detected
- Configurable sensitivity threshold
- Recording buffer (continues recording briefly after motion stops)
- Timestamp overlay on recordings
- Headless mode for server/background use

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python main.py
```

Press `q` to quit.

### Command Line Options

```
-c, --camera      Camera device ID (default: 0)
-t, --threshold   Motion sensitivity (default: 200000, lower = more sensitive)
-b, --buffer      Frames to keep recording after motion stops (default: 15)
-o, --output      Output directory for recordings (default: output_files)
--no-preview      Run without preview windows (headless mode)
```

### Examples

```bash
# Use camera 1 with higher sensitivity
python main.py --camera 1 --threshold 100000

# Run headless (no GUI) with custom output directory
python main.py --no-preview --output /path/to/recordings

# Very sensitive detection with longer recording buffer
python main.py -t 50000 -b 30
```

## Using as a Module

```python
from motion_detector import MotionDetector

with MotionDetector(
    camera_id=0,
    threshold=200000,
    show_preview=True
) as detector:
    detector.run()
```

## Output

Recordings are saved as `.avi` files in the output directory with sequential naming:
- `recording_0000.avi`
- `recording_0001.avi`
- etc.

## Requirements

- Python 3.7+
- OpenCV
- NumPy
- Webcam

## License

MIT

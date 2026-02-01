#!/usr/bin/env python3
"""
Motion Detection Camera - Entry Point

Detects movement via webcam and records video when motion is detected.

Usage:
    python main.py                    # Run with defaults
    python main.py --threshold 100000 # More sensitive
    python main.py --camera 1         # Use camera 1
    python main.py --no-preview       # Run headless
"""

import argparse
import sys

from motion_detector import MotionDetector


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Motion detection camera with automatic recording",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    
    parser.add_argument(
        "-c", "--camera",
        type=int,
        default=0,
        help="Camera device ID",
    )
    
    parser.add_argument(
        "-t", "--threshold",
        type=int,
        default=200000,
        help="Motion sensitivity threshold (lower = more sensitive)",
    )
    
    parser.add_argument(
        "-b", "--buffer",
        type=int,
        default=15,
        help="Frames to keep recording after motion stops",
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="output_files",
        help="Output directory for recordings",
    )
    
    parser.add_argument(
        "--no-preview",
        action="store_true",
        help="Run without preview windows (headless mode)",
    )
    
    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_args()
    
    try:
        with MotionDetector(
            camera_id=args.camera,
            threshold=args.threshold,
            record_buffer_frames=args.buffer,
            output_dir=args.output,
            show_preview=not args.no_preview,
        ) as detector:
            detector.run()
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 0
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

import os
import sys


def detect_os():
    """Detect operation system"""
    if sys.platform == "win32" or os.name == "nt":
        return "windows"
    return "linux"


if __name__ == "__main__":
    print(detect_os())

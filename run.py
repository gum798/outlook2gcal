#!/usr/bin/env python3
"""
Outlook to Google Calendar Sync Runner
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run the main function
from outlook2gcal import main

if __name__ == "__main__":
    main()
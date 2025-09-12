#!/usr/bin/env python3
"""
Quiet Outlook to Google Calendar Sync
Runs the sync in background without showing multiple windows
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    # Get the directory of this script
    script_dir = Path(__file__).parent
    run_script = script_dir / "run.py"
    
    # Prepare arguments (exclude the script name)
    args = sys.argv[1:] if len(sys.argv) > 1 else ['--sync']
    
    # Add quiet flag
    if '--quiet' not in args:
        args.append('--quiet')
    
    # Run the main script with minimized output
    try:
        # Set environment to reduce terminal output
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'
        
        # Run in background if possible
        result = subprocess.run([sys.executable, str(run_script)] + args,
                              env=env,
                              capture_output=False,
                              text=True)
        
        return result.returncode
        
    except Exception as e:
        print(f"Error running sync: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
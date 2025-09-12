#!/usr/bin/env python3
"""
Outlook to Google Calendar Sync Daemon
Runs the sync in background without any visible windows
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def main():
    # Get the directory of this script
    script_dir = Path(__file__).parent
    run_script = script_dir / "run.py"
    
    print("🚀 Starting Outlook2GCal background daemon...")
    print("📝 This will sync every 5 minutes in the background")
    print("⏹️  Press Ctrl+C to stop\n")
    
    try:
        # Set environment to reduce terminal output
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'
        
        # Run monitor mode in background
        result = subprocess.run([
            sys.executable, str(run_script), 
            '--monitor', 
            '--interval', '300',  # 5 minutes
            '--quiet'
        ], env=env)
        
        return result.returncode
        
    except KeyboardInterrupt:
        print("\n👋 Daemon stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Error running daemon: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
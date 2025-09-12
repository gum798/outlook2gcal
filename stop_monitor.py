#!/usr/bin/env python3
"""
Stop Outlook2GCal Background Monitor
"""

import os
import sys
import signal
import subprocess
from pathlib import Path

def main():
    print("🛑 Stopping Outlook2GCal background monitor...")
    
    stopped_count = 0
    
    # Method 1: Kill by PID file
    pid_file = Path("/tmp/outlook2gcal_monitor.pid")
    if pid_file.exists():
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process is still running
            try:
                os.kill(pid, 0)  # Test if process exists
                os.kill(pid, signal.SIGTERM)  # Gracefully terminate
                print(f"✅ Stopped monitor process (PID: {pid})")
                stopped_count += 1
                
                # Clean up PID file
                pid_file.unlink()
                
            except ProcessLookupError:
                print(f"⚠️  Process {pid} not found (already stopped)")
                pid_file.unlink()  # Clean up stale PID file
                
        except (ValueError, FileNotFoundError) as e:
            print(f"⚠️  Could not read PID file: {e}")
    
    # Method 2: Kill by process name (fallback)
    try:
        result = subprocess.run(['pgrep', '-f', 'run.py --monitor'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    pid = int(line.strip())
                    try:
                        os.kill(pid, signal.SIGTERM)
                        print(f"✅ Stopped additional monitor process (PID: {pid})")
                        stopped_count += 1
                    except ProcessLookupError:
                        pass
    except Exception as e:
        print(f"⚠️  Error searching for processes: {e}")
    
    # Method 3: Kill Python processes running monitor
    try:
        result = subprocess.run(['pgrep', '-f', 'python.*monitor'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    pid = int(line.strip())
                    try:
                        # Get process command to verify it's ours
                        ps_result = subprocess.run(['ps', '-p', str(pid), '-o', 'command='], 
                                                 capture_output=True, text=True)
                        if 'outlook2gcal' in ps_result.stdout.lower():
                            os.kill(pid, signal.SIGTERM)
                            print(f"✅ Stopped Outlook2GCal monitor (PID: {pid})")
                            stopped_count += 1
                    except (ProcessLookupError, subprocess.SubprocessError):
                        pass
    except Exception as e:
        print(f"⚠️  Error searching for Python processes: {e}")
    
    if stopped_count == 0:
        print("✨ No Outlook2GCal monitor processes found running")
    else:
        print(f"🎯 Stopped {stopped_count} monitor process(es)")
    
    print("\n📋 To check if any processes are still running:")
    print("   ps aux | grep outlook2gcal")
    print("\n🔄 To start monitoring again:")
    print("   python run.py --monitor --quiet")
    print("   or use the Outlook2GCal Sync app")

if __name__ == "__main__":
    main()
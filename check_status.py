#!/usr/bin/env python3
"""
Check Outlook2GCal Status - Quick status checker
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

def get_monitor_status():
    """Check if monitoring is active"""
    pid_file = Path("/tmp/outlook2gcal_monitor.pid")
    
    if not pid_file.exists():
        return False, None, "PID file not found"
    
    try:
        with open(pid_file, 'r') as f:
            pid = int(f.read().strip())
        
        # Check if process is running
        try:
            os.kill(pid, 0)  # Test if process exists
            return True, pid, "Active"
        except ProcessLookupError:
            # Clean up stale PID file
            pid_file.unlink()
            return False, pid, "Process not found (cleaned up)"
            
    except (ValueError, FileNotFoundError) as e:
        return False, None, f"Error reading PID: {e}"

def get_recent_logs():
    """Get recent log information"""
    log_files = list(Path("/tmp").glob("outlook2gcal_*.log"))
    if not log_files:
        return None, "No log files found"
    
    # Get most recent log
    latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
    mod_time = datetime.fromtimestamp(latest_log.stat().st_mtime)
    
    return latest_log, mod_time.strftime("%Y-%m-%d %H:%M:%S")

def check_outlook_running():
    """Check if Outlook is running"""
    try:
        result = subprocess.run(['pgrep', '-f', 'Microsoft Outlook'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def main():
    print("📊 Outlook2GCal Status Check")
    print("=" * 40)
    
    # Check monitoring status
    is_active, pid, status = get_monitor_status()
    
    if is_active:
        print(f"🟢 Monitoring: ACTIVE (PID: {pid})")
    else:
        print(f"🔴 Monitoring: STOPPED ({status})")
    
    # Check Outlook
    if check_outlook_running():
        print("📧 Outlook: RUNNING")
    else:
        print("❌ Outlook: NOT RUNNING")
    
    # Check recent logs
    log_file, log_time = get_recent_logs()
    if log_file:
        print(f"📝 Latest Log: {log_time}")
        
        # Show recent activity
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
            
            # Count recent activities
            sync_count = sum(1 for line in lines if "✅ Synced successfully" in line or "✨ No new events" in line)
            error_count = sum(1 for line in lines if "❌" in line or "ERROR" in line.upper())
            
            print(f"🔄 Recent Syncs: {sync_count}")
            if error_count > 0:
                print(f"⚠️  Recent Errors: {error_count}")
            
            # Show last few lines
            print(f"\n📄 Last Log Entries:")
            for line in lines[-3:]:
                if line.strip():
                    print(f"   {line.strip()}")
                    
        except Exception as e:
            print(f"⚠️  Could not read log: {e}")
    else:
        print(f"📝 Logs: {log_time}")
    
    # Show system commands
    print(f"\n🔧 Control Commands:")
    print(f"   Start: python run.py --monitor --quiet")
    print(f"   Stop:  python stop_monitor.py")
    print(f"   Sync:  python run.py --sync --quiet")
    
    # Return appropriate exit code
    return 0 if is_active else 1

if __name__ == "__main__":
    exit(main())
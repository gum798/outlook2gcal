#!/usr/bin/env python3
"""
Final Outlook to Google Calendar Sync Tool
"""

import subprocess
import json
import time
import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import re
import hashlib

# Google Calendar imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False

class OutlookReader:
    def __init__(self):
        self.check_outlook_running()
    
    def check_outlook_running(self):
        """Check if Outlook is running"""
        try:
            result = subprocess.run(['pgrep', '-f', 'Microsoft Outlook'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def run_applescript(self, script: str, timeout: int = 30) -> Optional[str]:
        """Run AppleScript and return result"""
        try:
            # Run osascript with proper shell environment to prevent new windows
            import os
            env = os.environ.copy()
            env['TERM'] = 'dumb'  # Prevent terminal interactions
            
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, timeout=timeout,
                                  env=env, 
                                  stdin=subprocess.DEVNULL,
                                  creationflags=0 if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0)
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                print(f"AppleScript error: {result.stderr.strip()}")
                return None
        except Exception as e:
            print(f"AppleScript failed: {e}")
            return None
    
    def get_events(self, days_back: int = 1, days_forward: int = 7) -> List[Dict]:
        """Get events from Outlook"""
        if not self.check_outlook_running():
            print("❌ Microsoft Outlook is not running. Please start Outlook first.")
            return []
        
        script = f'''
        tell application "Microsoft Outlook"
            set eventList to {{}}
            set calendarList to every calendar
            
            repeat with cal in calendarList
                try
                    set calendarName to name of cal
                    set recentEvents to every calendar event in cal
                    
                    repeat with evt in recentEvents
                        try
                            set eventTitle to subject of evt
                            set eventStart to start time of evt
                            set eventEnd to end time of evt
                            set eventLocation to ""
                            set eventOrganizer to ""
                            set isInvited to false
                            
                            try
                                set eventLocation to location of evt
                            end try
                            
                            -- Check if this is an invited event (not self-created)
                            try
                                set eventOrganizer to organizer of evt
                                -- If organizer exists and is different from current user, it's an invitation
                                if eventOrganizer is not missing value and eventOrganizer is not "" then
                                    set isInvited to true
                                end if
                            end try
                            
                            -- Get attendees
                            try
                                set eventAttendees to attendees of evt
                                if eventAttendees is not missing value and (count of eventAttendees) > 0 then
                                    set isInvited to true
                                end if
                            end try
                            
                            -- Also check if title contains invitation keywords
                            if eventTitle contains "[회의요청]" or eventTitle contains "초대" or eventTitle contains "Invitation" or eventTitle contains "invited" then
                                set isInvited to true
                            end if
                            
                            -- Only process invited events where user is recipient
                            if isInvited then
                                -- Get current date for comparison
                                set currentDate to current date
                                set startDiff to (eventStart - currentDate) / days
                                
                                -- Include events from past {days_back} days to future {days_forward} days
                                if startDiff > -{days_back} and startDiff < {days_forward} then
                                    -- Try to get additional info safely
                                    set eventContent to ""
                                    set eventImportance to ""
                                    
                                    try
                                        set eventContent to content of evt
                                    end try
                                    
                                    try
                                        set eventImportance to importance of evt as string
                                    end try
                                    
                                    set eventInfo to eventTitle & "|#|" & (eventStart as string) & "|#|" & (eventEnd as string) & "|#|" & calendarName & "|#|" & eventLocation & "|#|" & eventOrganizer & "|#|" & eventContent & "|#|" & eventImportance
                                    set end of eventList to eventInfo
                                end if
                            end if
                        on error
                            -- Skip problematic events
                        end try
                    end repeat
                on error
                    -- Skip problematic calendars
                end try
            end repeat
            
            -- Convert list to string
            set AppleScript's text item delimiters to "\\n"
            set resultString to eventList as string
            set AppleScript's text item delimiters to ""
            return resultString
        end tell
        '''
        
        print(f"📧 Fetching invited Outlook events ({days_back} days back, {days_forward} days forward)...")
        result = self.run_applescript(script, timeout=60)
        
        if not result:
            return []
        
        events = []
        for line in result.split('\n'):
            if line.strip():
                try:
                    parts = line.split('|#|')
                    if len(parts) >= 4:
                        # Parse dates properly
                        start_date = self.parse_date(parts[1])
                        end_date = self.parse_date(parts[2])
                        
                        # Create unique ID based on title, start time, and organizer (deterministic)
                        organizer_part = parts[5] if len(parts) > 5 else ''
                        hash_input = f'{parts[0]}-{start_date.isoformat()}-{organizer_part}'
                        unique_id = f"outlook-{hashlib.md5(hash_input.encode()).hexdigest()[:16]}"
                        
                        
                        events.append({
                            'id': unique_id,
                            'title': parts[0],
                            'start_date': start_date,
                            'end_date': end_date,
                            'location': parts[4] if len(parts) > 4 else '',
                            'calendar_title': parts[3],
                            'organizer': parts[5] if len(parts) > 5 else '',
                            'content': parts[6] if len(parts) > 6 else '',
                            'importance': parts[7] if len(parts) > 7 else '',
                            'all_day': False,
                            'last_modified': datetime.now(),
                            'notes': '',
                            'raw_start': parts[1],  # Keep original for debugging
                            'raw_end': parts[2],
                            'is_invited': True  # All events from this filter are invited events
                        })
                except Exception as e:
                    print(f"⚠️  Error parsing event: {e}")
                    continue
        
        return events
    
    def parse_date(self, date_str: str) -> datetime:
        """Parse AppleScript date string"""
        try:
            # Remove day of week prefix
            date_str = re.sub(r'(월요일|화요일|수요일|목요일|금요일|토요일|일요일|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s*', '', date_str)
            
            # Korean date parsing with regex
            korean_pattern = r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일\s*(오전|오후)\s*(\d{1,2}):(\d{2}):(\d{2})'
            match = re.search(korean_pattern, date_str)
            
            if match:
                year = int(match.group(1))
                month = int(match.group(2))
                day = int(match.group(3))
                am_pm = match.group(4)
                hour = int(match.group(5))
                minute = int(match.group(6))
                second = int(match.group(7))
                
                # Convert to 24-hour format
                if am_pm == '오후' and hour != 12:
                    hour += 12
                elif am_pm == '오전' and hour == 12:
                    hour = 0
                
                return datetime(year, month, day, hour, minute, second)
            
            # Fallback to current time if parsing fails
            print(f"Could not parse date: '{date_str}'")
            return datetime.now()
            
        except Exception as e:
            print(f"Date parsing error for '{date_str}': {e}")
            return datetime.now()

class GoogleSync:
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self, credentials_file: str = "config/credentials.json", token_file: str = "config/token.json"):
        self.credentials_file = Path(credentials_file)
        self.token_file = Path(token_file)
        self.service = None
        self.calendar_id = 'primary'
        
        if GOOGLE_API_AVAILABLE:
            self._authenticate()
            # Set default to "2.업무" calendar
            self._set_default_work_calendar()
    
    def _authenticate(self):
        """Authenticate with Google Calendar API"""
        creds = None
        
        if self.token_file.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_file), self.SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not self.credentials_file.exists():
                    print(f"❌ {self.credentials_file} not found")
                    return
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_file), self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('calendar', 'v3', credentials=creds)
        print("✅ Google Calendar authenticated")
    
    def _set_default_work_calendar(self):
        """Set default calendar to '2.업무' if available"""
        if not self.service:
            return
        
        try:
            calendars = self.list_calendars()
            for cal in calendars:
                if cal['summary'] == '2.업무':
                    self.calendar_id = cal['id']
                    print(f"🎯 Default calendar set to: 2.업무")
                    break
        except Exception as e:
            print(f"Could not set default work calendar: {e}")
    
    def list_calendars(self) -> List[Dict]:
        """List Google calendars"""
        if not self.service:
            return []
        
        try:
            calendars_result = self.service.calendarList().list().execute()
            return calendars_result.get('items', [])
        except HttpError as error:
            print(f'❌ Google Calendar error: {error}')
            return []
    
    def create_event(self, outlook_event: Dict) -> Optional[str]:
        """Create event in Google Calendar"""
        if not self.service:
            return None
        
        try:
            # Build clean description
            description_parts = [f"🎯 Invited Event from Outlook Calendar: {outlook_event['calendar_title']}"]
            
            if outlook_event.get('organizer'):
                description_parts.append(f"👤 Organizer: {outlook_event['organizer']}")
            
            google_event = {
                'summary': f"📧 {outlook_event['title']}",  # Add invitation icon
                'description': "\n".join(description_parts),
                'location': outlook_event.get('location', ''),
                'start': {
                    'dateTime': outlook_event['start_date'].isoformat(),
                    'timeZone': 'Asia/Seoul',
                },
                'end': {
                    'dateTime': outlook_event['end_date'].isoformat(),
                    'timeZone': 'Asia/Seoul',
                }
            }
            
            event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=google_event
            ).execute()
            
            return event['id']
            
        except HttpError as error:
            print(f'❌ Error creating event "{outlook_event["title"]}": {error}')
            print(f'   Error details: {error.content}')
            return None
    
    def check_event_exists(self, outlook_event: Dict) -> Optional[str]:
        """Check if similar event already exists in Google Calendar
        Returns: Google event ID if exists, None otherwise"""
        if not self.service:
            return None
        
        try:
            # Search for events with same title around the same time
            start_time = outlook_event['start_date']
            
            # Search same day (broader range for safety)
            same_day_start = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
            same_day_end = start_time.replace(hour=23, minute=59, second=59, microsecond=0)
            
            time_min = same_day_start.isoformat() + '+09:00'
            time_max = same_day_end.isoformat() + '+09:00'
            
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Check if any event matches closely
            target_title = outlook_event['title']
            
            for event in events:
                event_title = event.get('summary', '')
                # Remove the 📧 prefix for comparison
                clean_title = event_title.replace('📧 ', '')
                
                if clean_title == target_title:
                    return event.get('id')  # Return Google event ID
            
            return None
            
        except HttpError as error:
            print(f'⚠️  Error checking for existing event: {error}')
            return None
    
    def delete_event(self, google_event_id: str) -> bool:
        """Delete event from Google Calendar"""
        if not self.service:
            return False
        
        try:
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=google_event_id
            ).execute()
            return True
        except HttpError as error:
            if error.resp.status == 404:
                # Event already deleted
                return True
            print(f'❌ Error deleting event: {error}')
            return False

class SyncMonitor:
    def __init__(self, state_file: str = "config/sync_state.json"):
        self.state_file = Path(state_file)
        self.synced_events = {}  # Changed to dict to store event date info
        self.load_state()
    
    def load_state(self):
        """Load sync state"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    # Handle both old format (list) and new format (dict)
                    synced_events_data = state.get('synced_events', [])
                    if isinstance(synced_events_data, list):
                        # Convert old format to new format
                        self.synced_events = {event_id: {'synced_date': datetime.now().isoformat()} 
                                            for event_id in synced_events_data}
                        print(f"📋 Converted {len(self.synced_events)} events from old format")
                    else:
                        # New format with date info
                        self.synced_events = synced_events_data
                        print(f"📋 Loaded {len(self.synced_events)} previously synced events")
                    
                    # Migrate old hash-based IDs to new MD5-based IDs
                    self.migrate_old_ids()
                    
                    # Clean up old events (older than 2 months)
                    self.cleanup_old_events()
            except Exception as e:
                print(f"⚠️  Error loading state: {e}")
                self.synced_events = {}
    
    def migrate_old_ids(self):
        """Migrate old hash-based IDs to new MD5-based IDs"""
        migrated_events = {}
        migration_count = 0
        
        for old_id, event_info in list(self.synced_events.items()):
            # Check if this is an old-style ID (negative number)
            if old_id.startswith('outlook--') and old_id[9:].lstrip('-').isdigit():
                # Try to generate new ID from stored info
                title = event_info.get('title', '')
                event_date = event_info.get('event_date', '')
                
                # We don't have organizer info in old data, so we'll have to skip for now
                # and let the sync process handle re-identification
                print(f"   🔄 Found old-style ID, will be re-identified: {title}")
                migration_count += 1
            else:
                # Keep new-style IDs as-is
                migrated_events[old_id] = event_info
        
        if migration_count > 0:
            print(f"   📝 {migration_count} old IDs found - will be re-identified during sync")
            # Don't remove old IDs yet - let them be handled by normal sync logic
    
    def save_state(self):
        """Save sync state"""
        try:
            state = {'synced_events': self.synced_events}
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"⚠️  Error saving state: {e}")
    
    def cleanup_old_events(self):
        """Remove events older than 2 months"""
        cutoff_date = datetime.now() - timedelta(days=60)  # 2 months
        old_events = []
        
        for event_id, event_info in list(self.synced_events.items()):
            try:
                synced_date = datetime.fromisoformat(event_info.get('synced_date', ''))
                if synced_date < cutoff_date:
                    old_events.append(event_id)
            except (ValueError, TypeError):
                # Remove invalid entries
                old_events.append(event_id)
        
        for event_id in old_events:
            del self.synced_events[event_id]
        
        if old_events:
            print(f"🧹 Cleaned up {len(old_events)} old event IDs")
    
    def get_synced_event_ids(self) -> set:
        """Get set of all synced event IDs"""
        return set(self.synced_events.keys())
    
    def remove_synced_event(self, event_id: str):
        """Remove event from synced events"""
        if event_id in self.synced_events:
            del self.synced_events[event_id]
    
    def find_matching_old_event(self, new_event: Dict) -> Optional[str]:
        """Find an old event that matches the new event by title, date, and organizer"""
        for old_id, old_info in self.synced_events.items():
            # Check if this is an old-style ID
            if old_id.startswith('outlook--') and old_id[9:].lstrip('-').isdigit():
                # Compare title, date, and organizer
                if (old_info.get('title', '').strip() == new_event['title'].strip() and
                    old_info.get('event_date', '') == new_event['start_date'].isoformat()):
                    return old_id
        return None
    
    def update_event_id(self, old_id: str, new_id: str, new_event: Dict):
        """Update an event's ID from old format to new format"""
        if old_id in self.synced_events:
            # Copy old data to new ID
            old_data = self.synced_events[old_id].copy()
            # Update with new information
            old_data.update({
                'synced_date': datetime.now().isoformat(),
                'event_date': new_event['start_date'].isoformat(),
                'title': new_event['title']
            })
            
            # Add under new ID
            self.synced_events[new_id] = old_data
            # Remove old ID
            del self.synced_events[old_id]
            
            print(f"   ✅ Updated event ID: {old_id} -> {new_id}")
    
    def is_synced(self, event: Dict) -> bool:
        """Check if event was already synced"""
        return event['id'] in self.synced_events
    
    def mark_synced(self, event: Dict, google_event_id: str = None):
        """Mark event as synced"""
        if google_event_id is None:
            print(f"⚠️  Warning: Marking event as synced without Google event ID: {event['title']}")
        
        self.synced_events[event['id']] = {
            'synced_date': datetime.now().isoformat(),
            'event_date': event['start_date'].isoformat(),
            'title': event['title'],
            'google_event_id': google_event_id
        }

def main():
    parser = argparse.ArgumentParser(description='Sync Outlook events to Google Calendar')
    parser.add_argument('--setup', action='store_true', help='Run setup check')
    parser.add_argument('--sync', action='store_true', help='Sync events once')
    parser.add_argument('--monitor', action='store_true', help='Start continuous monitoring')
    parser.add_argument('--interval', type=int, default=300, help='Monitor interval in seconds')
    parser.add_argument('--calendar', type=str, help='Target Google Calendar ID')
    parser.add_argument('--quiet', action='store_true', help='Run in quiet mode (minimize window)')
    
    args = parser.parse_args()
    
    # Minimize window if running in quiet mode or if GUI detected
    if args.quiet or (not sys.stdin.isatty()):
        try:
            import os
            # Try to minimize the current terminal window (macOS)
            os.system('osascript -e "tell application \\"System Events\\" to set visible of process \\"Terminal\\" to false" 2>/dev/null || true')
        except:
            pass
    
    print("🔄 Outlook to Google Calendar Sync")
    print("=" * 40)
    
    # Initialize components
    outlook = OutlookReader()
    google = GoogleSync()
    monitor = SyncMonitor()
    
    # Setup check
    if args.setup or not any([args.sync, args.monitor]):
        print("\\n📋 Setup Check:")
        
        # Check Outlook
        if outlook.check_outlook_running():
            print("✅ Microsoft Outlook: Running")
        else:
            print("❌ Microsoft Outlook: Not running")
        
        # Check Google Calendar
        calendars = google.list_calendars()
        if calendars:
            print(f"✅ Google Calendar: {len(calendars)} calendars available")
            for cal in calendars[:5]:  # Show first 5
                primary = " (PRIMARY)" if cal.get('primary') else ""
                print(f"   - {cal['summary']}{primary}")
        else:
            print("❌ Google Calendar: Not accessible")
        
        if args.setup:
            return
    
    # Set target calendar
    if args.calendar:
        # Check if it's a calendar name (not ID)
        if '@group.calendar.google.com' not in args.calendar and '@gmail.com' not in args.calendar:
            # Find calendar ID by name
            calendars = google.list_calendars()
            calendar_id = None
            for cal in calendars:
                if cal['summary'] == args.calendar:
                    calendar_id = cal['id']
                    break
            
            if calendar_id:
                google.calendar_id = calendar_id
                print(f"🎯 Target calendar: {args.calendar} ({calendar_id})")
            else:
                print(f"❌ Calendar '{args.calendar}' not found")
                print("Available calendars:")
                for cal in calendars:
                    print(f"  - {cal['summary']}")
                return
        else:
            google.calendar_id = args.calendar
            print(f"🎯 Target calendar: {args.calendar}")
    
    # Sync function
    def sync_events():
        print(f"\\n🔍 [{datetime.now().strftime('%H:%M:%S')}] Checking for new invited events...")
        
        events = outlook.get_events(days_back=1, days_forward=7)
        print(f"📧 Found {len(events)} invited Outlook events")
        
        # Debug: Show stored events
        print(f"   📦 Stored Events ({len(monitor.synced_events)}):")
        for stored_id, stored_info in monitor.synced_events.items():
            print(f"      - {stored_id}: {stored_info.get('title', 'Unknown')}")
        
        # Debug: Show detailed event information
        if events:
            print("   📋 Detailed Event Information:")
            for event in events:
                print(f"   🔍 EVENT ID: {event['id']}")
                print(f"   📝 Title: {event['title']}")
                print(f"   📅 Start: {event['start_date']} ({event['raw_start']})")
                print(f"   📅 End: {event['end_date']} ({event['raw_end']})")
                print(f"   📍 Location: {event['location']}")
                print(f"   📊 Calendar: {event['calendar_title']}")
                print(f"   👤 Organizer: {event['organizer']}")
                print(f"   📄 Content: {event['content'][:100]}{'...' if len(event['content']) > 100 else ''}")
                print(f"   ⚡ Importance: {event['importance']}")
                print(f"   ✅ Is Invited: {event['is_invited']}")
                print(f"   📝 Last Modified: {event['last_modified']}")
                print("   " + "="*50)
        
        # Filter out events that are already synced or exist in Google Calendar
        new_events = []
        for event in events:
            if monitor.is_synced(event):
                print(f"   ⏭️  Already synced: {event['title']}")
                continue
            
            # Check for old-style ID matches (same title + date + organizer)
            old_event_match = monitor.find_matching_old_event(event)
            if old_event_match:
                print(f"   🔄 Found matching old event, updating ID: {event['title']}")
                # Update the stored event with new ID
                monitor.update_event_id(old_event_match, event['id'], event)
                continue
            
            existing_google_event_id = google.check_event_exists(event)
            if existing_google_event_id:
                print(f"   🔄 Event already exists in Google Calendar: {event['title']}")
                monitor.mark_synced(event, existing_google_event_id)  # Mark with actual Google event ID
                continue
            new_events.append(event)
        
        if new_events:
            print(f"🆕 {len(new_events)} new events to sync:")
            for event in new_events:
                print(f"   📝 {event['title']} ({event['calendar_title']})")
                
                google_event_id = google.create_event(event)
                if google_event_id:
                    monitor.mark_synced(event, google_event_id)
                    print(f"   ✅ Synced successfully")
                else:
                    print(f"   ❌ Sync failed")
            
            monitor.save_state()
        else:
            print("✨ No new events to sync")
        
        # Check for deleted events (compare current events with previously synced events)
        current_event_ids = {event['id'] for event in events}
        synced_event_ids = monitor.get_synced_event_ids()
        deleted_event_ids = synced_event_ids - current_event_ids
        
        if deleted_event_ids:
            print(f"🗑️  Found {len(deleted_event_ids)} deleted events in Outlook")
            for event_id in deleted_event_ids:
                event_info = monitor.synced_events.get(event_id, {})
                google_event_id = event_info.get('google_event_id')
                event_title = event_info.get('title', 'Unknown')
                
                if google_event_id:
                    if google.delete_event(google_event_id):
                        print(f"   🗑️  Deleted from Google Calendar: {event_title}")
                        monitor.remove_synced_event(event_id)
                    else:
                        print(f"   ❌ Failed to delete: {event_title}")
                else:
                    # Remove from sync state even if no Google event ID
                    print(f"   🗑️  Removed from sync state: {event_title}")
                    monitor.remove_synced_event(event_id)
            
            monitor.save_state()
    
    # Run sync
    if args.sync:
        sync_events()
    
    # Monitor mode
    if args.monitor:
        print(f"\\n🔄 Starting continuous monitoring (every {args.interval}s)")
        print("Press Ctrl+C to stop")
        
        # Send initial notification (macOS)
        try:
            import os
            os.system('osascript -e "display notification \\"🔄 Outlook2GCal monitoring started\\" with title \\"Outlook2GCal Sync\\""')
        except:
            pass
        
        sync_count = 0
        try:
            while True:
                sync_count += 1
                print(f"\\n🔄 Sync cycle #{sync_count}")
                sync_events()
                
                # Send periodic status notification (every 5 cycles)
                if sync_count % 5 == 0:
                    try:
                        os.system(f'osascript -e "display notification \\"✅ Monitoring active - Cycle #{sync_count}\\" with title \\"Outlook2GCal Sync\\""')
                    except:
                        pass
                
                print(f"😴 Sleeping for {args.interval} seconds...")
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\\n👋 Monitoring stopped")
            # Send stop notification
            try:
                os.system('osascript -e "display notification \\"🛑 Monitoring stopped\\" with title \\"Outlook2GCal Sync\\""')
            except:
                pass

if __name__ == "__main__":
    main()
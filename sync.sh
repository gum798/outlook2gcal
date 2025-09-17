#!/bin/bash
# Outlook to Google Calendar Sync Helper Script

cd "$(dirname "$0")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔄 Outlook2GCal Sync Helper${NC}"
echo "================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo "Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check command line arguments
case "$1" in
    "setup"|"--setup")
        echo -e "${YELLOW}📋 Running setup check...${NC}"
        python3 run.py --setup
        ;;
    "sync"|"--sync")
        echo -e "${YELLOW}🔄 Running one-time sync...${NC}"
        python3 run.py --sync
        ;;
    "monitor"|"--monitor")
        echo -e "${YELLOW}🔄 Starting continuous monitoring...${NC}"
        python3 run.py --monitor --interval "${2:-300}"
        ;;
    "quiet"|"--quiet")
        echo -e "${YELLOW}🔇 Running quiet sync...${NC}"
        python3 run.py --sync --quiet
        ;;
    *)
        echo -e "${GREEN}Usage:${NC}"
        echo "  ./sync.sh setup     - Check system setup"
        echo "  ./sync.sh sync      - Run one-time sync"
        echo "  ./sync.sh monitor   - Start continuous monitoring (default: 5 min intervals)"
        echo "  ./sync.sh monitor 60 - Start monitoring with custom interval (seconds)"
        echo "  ./sync.sh quiet     - Run quiet sync (minimize window)"
        echo ""
        echo -e "${BLUE}Examples:${NC}"
        echo "  ./sync.sh setup     # Check if everything is working"
        echo "  ./sync.sh sync      # Sync once and exit"
        echo "  ./sync.sh monitor   # Monitor continuously every 5 minutes"
        echo "  ./sync.sh monitor 120 # Monitor every 2 minutes"
        ;;
esac
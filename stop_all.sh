#!/bin/bash
# ========================================
# ShopEase - Stop All Servers
# ========================================
# Use this before switching between development and production modes

echo "========================================"
echo "  Stopping All ShopEase Servers"
echo "========================================"

# Kill Gunicorn processes
if pgrep -f "gunicorn" > /dev/null; then
    pkill -f "gunicorn" 2>/dev/null
    echo "  ✓ Gunicorn servers stopped"
else
    echo "  - No Gunicorn processes running"
fi

# Kill Django runserver processes
if pgrep -f "manage.py runserver" > /dev/null; then
    pkill -f "manage.py runserver" 2>/dev/null
    echo "  ✓ Django dev servers stopped"
else
    echo "  - No Django dev servers running"
fi

# Kill any Python processes using our ports
for port in 8000 8080 9000; do
    pid=$(lsof -t -i:$port 2>/dev/null)
    if [ -n "$pid" ]; then
        kill $pid 2>/dev/null
        echo "  ✓ Killed process on port $port"
    fi
done

echo ""
echo "All servers stopped. Ready to switch modes."
echo "========================================"

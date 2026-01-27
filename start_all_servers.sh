#!/bin/bash
# ========================================
# ShopEase Development Mode Startup Script
# ========================================
# Starts all 3 Django servers with DEBUG=True:
# - Customer: port 8000
# - Admin: port 8080
# - Docs: port 9000
#
# Use this for LOCAL DEVELOPMENT (HTTP)
# For production (HTTPS), use start_production.sh

echo "========================================="
echo "  Starting ShopEase DEVELOPMENT Mode"
echo "========================================="

# Base directory
BASE_DIR="/mnt/c/Users/Prathmesh D Birajdar/OneDrive/Desktop/ShopEase"
SHOPEASE_DIR="$BASE_DIR/shopease"
DOCS_DIR="$BASE_DIR/shopeasedocs"
VENV_DIR="$BASE_DIR/venv"

# Step 0: Stop any running servers first
echo ""
echo "[0/5] Stopping existing servers..."
pkill -f "gunicorn" 2>/dev/null
pkill -f "manage.py runserver" 2>/dev/null
sleep 1
echo "  ✓ Existing servers stopped"

# Step 0.5: Set DEBUG=True for development mode
echo ""
echo "[0.5/5] Setting DEBUG=True for development..."
sed -i 's/DEBUG=False/DEBUG=True/' "$SHOPEASE_DIR/.env" 2>/dev/null
sed -i 's/DEBUG=False/DEBUG=True/' "$DOCS_DIR/.env" 2>/dev/null
echo "  ✓ DEBUG=True set (static files will be served by Django)"

# Activate virtual environment
source "$VENV_DIR/bin/activate"

echo ""
echo "[1/5] Starting Redis..."
redis-cli ping > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✓ Redis already running"
else
    echo "  Starting Redis server..."
    sudo service redis-server start
fi

echo ""
echo "[2/5] Collecting static files..."
cd "$SHOPEASE_DIR"
python manage.py collectstatic --noinput > /dev/null 2>&1
echo "  ✓ Static files collected"

echo ""
echo "[3/5] Starting Customer Server (port 8000)..."
cd "$SHOPEASE_DIR"
python manage.py runserver 0.0.0.0:8000 --settings=config.settings.customer > /tmp/shopease_customer.log 2>&1 &
CUSTOMER_PID=$!
echo "  ✓ Customer server started (PID: $CUSTOMER_PID)"

echo ""
echo "[4/5] Starting Admin Server (port 8080)..."
python manage.py runserver 0.0.0.0:8080 --settings=config.settings.admin > /tmp/shopease_admin.log 2>&1 &
ADMIN_PID=$!
echo "  ✓ Admin server started (PID: $ADMIN_PID)"

echo ""
echo "[5/5] Starting Docs Server (port 9000)..."
cd "$DOCS_DIR"
python manage.py runserver 0.0.0.0:9000 > /tmp/shopease_docs.log 2>&1 &
DOCS_PID=$!
echo "  ✓ Docs server started (PID: $DOCS_PID)"

echo ""
echo "========================================="
echo "  All Servers Started!"
echo "========================================="
echo ""
echo "Access URLs:"
echo "  Customer: http://localhost:8000"
echo "  Admin:    http://localhost:8080"
echo "  Docs:     http://localhost:9000"
echo ""
echo "To go online, run in another terminal:"
echo "  ngrok http 8000"
echo ""
echo "View logs:"
echo "  tail -f /tmp/shopease_customer.log"
echo "  tail -f /tmp/shopease_admin.log"
echo "  tail -f /tmp/shopease_docs.log"
echo ""
echo "To stop all servers:"
echo "  kill $CUSTOMER_PID $ADMIN_PID $DOCS_PID"
echo ""

# Keep script running to show logs
echo "Press Ctrl+C to stop all servers..."
wait

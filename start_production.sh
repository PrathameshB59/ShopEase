#!/bin/bash
# ========================================
# ShopEase Production Startup Script
# ========================================
# Architecture: Ngrok -> Nginx -> Gunicorn -> Django
#
# Use this for PRODUCTION (HTTPS via Ngrok)
# For development (HTTP), use start_all_servers.sh
#
# Usage: bash start_production.sh
# ========================================

echo "========================================"
echo "  ShopEase PRODUCTION Startup"
echo "========================================"

# Base paths
BASE_DIR="/mnt/c/Users/Prathmesh D Birajdar/OneDrive/Desktop/ShopEase"
SHOPEASE_DIR="$BASE_DIR/shopease"
DOCS_DIR="$BASE_DIR/shopeasedocs"
VENV_DIR="$BASE_DIR/venv"

# ========================================
# Step 0: Stop existing servers
# ========================================
echo ""
echo "[0/7] Stopping existing servers..."
pkill -f "gunicorn" 2>/dev/null
pkill -f "manage.py runserver" 2>/dev/null
sleep 1
echo "  ✓ Existing servers stopped"

# ========================================
# Step 0.5: Set DEBUG=False for production
# ========================================
echo ""
echo "[0.5/7] Setting DEBUG=False for production..."
sed -i 's/DEBUG=True/DEBUG=False/' "$SHOPEASE_DIR/.env" 2>/dev/null
sed -i 's/DEBUG=True/DEBUG=False/' "$DOCS_DIR/.env" 2>/dev/null
echo "  ✓ DEBUG=False set (static files served by Nginx)"

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# ========================================
# Step 1: Setup Nginx
# ========================================
echo ""
echo "[1/7] Setting up Nginx..."
sudo cp "$BASE_DIR/nginx_shopease.conf" /etc/nginx/sites-available/shopease
sudo rm -f /etc/nginx/sites-enabled/default 2>/dev/null
sudo ln -sf /etc/nginx/sites-available/shopease /etc/nginx/sites-enabled/shopease
echo "  ✓ Nginx config installed"

# ========================================
# Step 2: Start Redis
# ========================================
echo ""
echo "[2/6] Starting Redis..."
redis-cli ping > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "  ✓ Redis already running"
else
    sudo service redis-server start
    sleep 2
    redis-cli ping > /dev/null 2>&1 && echo "  ✓ Redis started" || echo "  ✗ Redis failed to start"
fi

# ========================================
# Step 3: Collect Static Files
# ========================================
echo ""
echo "[3/6] Collecting static files..."
cd "$SHOPEASE_DIR"
python manage.py collectstatic --noinput --settings=config.settings.customer > /dev/null 2>&1
echo "  ✓ Static files collected"

# ========================================
# Step 4: Start Gunicorn Servers
# ========================================
echo ""
echo "[4/6] Starting Gunicorn servers..."

# Kill any existing Gunicorn processes
pkill -f "gunicorn.*shopease" 2>/dev/null
sleep 1

# Customer Server (Gunicorn on 8001, Nginx proxies from 80)
cd "$SHOPEASE_DIR"
gunicorn config.wsgi_customer:application \
    --bind 127.0.0.1:8001 \
    --workers 3 \
    --timeout 120 \
    --access-logfile /tmp/gunicorn_customer_access.log \
    --error-logfile /tmp/gunicorn_customer_error.log \
    --capture-output \
    --daemon \
    --pid /tmp/gunicorn_customer.pid
echo "  ✓ Customer server started (Gunicorn:8001 → Nginx:80)"

# Admin Server (Gunicorn on 8081, Nginx proxies from 8080)
gunicorn config.wsgi_admin:application \
    --bind 127.0.0.1:8081 \
    --workers 2 \
    --timeout 120 \
    --access-logfile /tmp/gunicorn_admin_access.log \
    --error-logfile /tmp/gunicorn_admin_error.log \
    --capture-output \
    --daemon \
    --pid /tmp/gunicorn_admin.pid
echo "  ✓ Admin server started (Gunicorn:8081 → Nginx:8080)"

# Docs Server (Gunicorn on 9001, Nginx proxies from 9000)
cd "$DOCS_DIR"
gunicorn shopeasedocs.wsgi:application \
    --bind 127.0.0.1:9001 \
    --workers 2 \
    --timeout 60 \
    --access-logfile /tmp/gunicorn_docs_access.log \
    --error-logfile /tmp/gunicorn_docs_error.log \
    --capture-output \
    --daemon \
    --pid /tmp/gunicorn_docs.pid
echo "  ✓ Docs server started (Gunicorn:9001 → Nginx:9000)"

# ========================================
# Step 5: Start Nginx
# ========================================
echo ""
echo "[5/6] Starting Nginx..."
sudo nginx -t > /dev/null 2>&1
if [ $? -eq 0 ]; then
    sudo service nginx restart
    echo "  ✓ Nginx started"
else
    echo "  ✗ Nginx config error!"
    sudo nginx -t
    exit 1
fi

# ========================================
# Step 6: Verify All Services
# ========================================
echo ""
echo "[6/6] Verifying services..."
sleep 2

# Check Gunicorn (internal ports)
curl -s http://127.0.0.1:8001 > /dev/null && echo "  ✓ Gunicorn Customer (8001): Running" || echo "  ✗ Gunicorn Customer (8001): Failed"
curl -s http://127.0.0.1:8081 > /dev/null && echo "  ✓ Gunicorn Admin (8081): Running" || echo "  ✗ Gunicorn Admin (8081): Failed"
curl -s http://127.0.0.1:9001 > /dev/null && echo "  ✓ Gunicorn Docs (9001): Running" || echo "  ✗ Gunicorn Docs (9001): Failed"

# Check Nginx (external ports)
curl -s http://localhost > /dev/null && echo "  ✓ Nginx Customer (80): Running" || echo "  ✗ Nginx Customer (80): Failed"
curl -s http://localhost:8080 > /dev/null && echo "  ✓ Nginx Admin (8080): Running" || echo "  ✗ Nginx Admin (8080): Failed"
curl -s http://localhost:9000 > /dev/null && echo "  ✓ Nginx Docs (9000): Running" || echo "  ✗ Nginx Docs (9000): Failed"

echo ""
echo "========================================"
echo "  All Services Started!"
echo "========================================"
echo ""
echo "Local Access:"
echo "  Customer: http://localhost"
echo "  Admin:    http://localhost:8080"
echo "  Docs:     http://localhost:9000"
echo ""
echo "To go PUBLIC with Ngrok, run in another terminal:"
echo "  ngrok http 80"
echo ""
echo "View logs:"
echo "  tail -f /tmp/gunicorn_customer_error.log"
echo "  tail -f /tmp/gunicorn_admin_error.log"
echo "  tail -f /var/log/nginx/error.log"
echo ""
echo "To stop all services:"
echo "  bash stop_production.sh"
echo ""

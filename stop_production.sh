#!/bin/bash
# ========================================
# ShopEase Production Stop Script
# ========================================

echo "========================================"
echo "  Stopping ShopEase Production"
echo "========================================"

# Stop Gunicorn servers
echo ""
echo "[1/3] Stopping Gunicorn servers..."
pkill -f "gunicorn.*shopease" 2>/dev/null
pkill -f "gunicorn.*shopeasedocs" 2>/dev/null

# Remove PID files
rm -f /tmp/gunicorn_customer.pid /tmp/gunicorn_admin.pid /tmp/gunicorn_docs.pid 2>/dev/null
echo "  ✓ Gunicorn stopped"

# Stop Nginx
echo ""
echo "[2/3] Stopping Nginx..."
sudo service nginx stop
echo "  ✓ Nginx stopped"

# Optional: Stop Redis
echo ""
echo "[3/3] Redis status..."
echo "  (Redis left running for other apps)"
echo "  To stop Redis: sudo service redis-server stop"

echo ""
echo "========================================"
echo "  All Services Stopped"
echo "========================================"

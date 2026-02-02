"""
========================================
GUNICORN CONFIGURATION FOR SHOPEASE
CUSTOMER SERVER
========================================

Production-grade WSGI server configuration.

Workers: 4 (2 * CPU cores + 1)
Threads: 2 per worker
Max Requests: 1000 (prevents memory leaks)
"""

import multiprocessing
import os

# Bind to all interfaces (allows Nginx to connect)
bind = "127.0.0.1:8000"

# Worker configuration
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
threads = 2

# Max requests before worker restart (prevents memory leaks)
max_requests = 1000
max_requests_jitter = 50

# Timeouts
timeout = 30
keepalive = 2

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "shopease_customer"

# Server mechanics
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# SSL (for direct HTTPS - not needed with Nginx)
# keyfile = None
# certfile = None

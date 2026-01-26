"""
========================================
GUNICORN CONFIGURATION FOR SHOPEASE
ADMIN SERVER
========================================

Production-grade WSGI server configuration for admin panel.
"""

import multiprocessing

# Bind to admin port
bind = "127.0.0.1:8080"

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
proc_name = "shopease_admin"

# Server mechanics
daemon = False
pidfile = None

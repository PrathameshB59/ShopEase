"""
========================================
GUNICORN CONFIGURATION FOR SHOPEASEDOCS
========================================

Production-grade WSGI server configuration for documentation server.
"""

import multiprocessing

# Bind to docs port
bind = "127.0.0.1:9000"

# Worker configuration (fewer workers for docs - less traffic)
workers = 2
worker_class = "sync"
worker_connections = 1000
threads = 2

# Max requests before worker restart
max_requests = 1000
max_requests_jitter = 50

# Timeouts
timeout = 30
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "shopease_docs"

# Server mechanics
daemon = False
pidfile = None

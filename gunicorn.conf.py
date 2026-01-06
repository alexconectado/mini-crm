# Gunicorn Configuration for Production

import multiprocessing
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Server socket
bind = os.environ.get("GUNICORN_BIND", "127.0.0.1:8000")
backlog = 2048

# Worker processes
workers = int(os.environ.get("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2

# Logging
accesslog = os.environ.get("GUNICORN_ACCESS_LOG", "/var/log/gunicorn/access.log")
errorlog = os.environ.get("GUNICORN_ERROR_LOG", "/var/log/gunicorn/error.log")
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "mini-crm"

# SSL (if using nginx reverse proxy, disable this)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"
# ssl_version = ssl.PROTOCOL_TLSv1_2

# Server mechanics
daemon = False
pidfile = "/var/run/gunicorn.pid"
umask = 0o022
user = None
group = None
tmp_upload_dir = None

# SSL Configuration (uncomment if using gunicorn directly with SSL)
# Recommended: Use nginx as reverse proxy instead
# ca_certs = "/path/to/ca-bundle.crt"

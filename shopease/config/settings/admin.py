"""
Admin settings - runs on port 8080
"""
from .base import *

SERVER_TYPE = 'admin'

# Cookie names - Different for each server to prevent conflicts
SESSION_COOKIE_NAME = 'shopease_admin_sessionid'
CSRF_COOKIE_NAME = 'shopease_admin_csrftoken'

ROOT_URLCONF = 'config.urls_admin'
WSGI_APPLICATION = 'config.wsgi_admin.application'

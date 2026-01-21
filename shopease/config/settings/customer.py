"""
Customer settings - runs on port 8000
"""
from .base import *

SERVER_TYPE = 'customer'

# Cookie names - Different for each server to prevent conflicts
SESSION_COOKIE_NAME = 'shopease_customer_sessionid'
CSRF_COOKIE_NAME = 'shopease_customer_csrftoken'

ROOT_URLCONF = 'config.urls_customer'
WSGI_APPLICATION = 'config.wsgi_customer.application'

"""
Customer settings - runs on port 8000
"""
from .base import *

ROOT_URLCONF = 'config.urls_customer'
WSGI_APPLICATION = 'config.wsgi_customer.application'

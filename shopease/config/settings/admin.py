"""
Admin settings - runs on port 8080
"""
from .base import *

ROOT_URLCONF = 'config.urls_admin'
WSGI_APPLICATION = 'config.wsgi_admin.application'

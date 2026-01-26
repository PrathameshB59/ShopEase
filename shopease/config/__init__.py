"""
ShopEase Config Package

Configures Celery to work with Django.
"""

# Tell Django to use PyMySQL as MySQL adapter
import pymysql
pymysql.install_as_MySQLdb()

# Ensure Celery app is loaded when Django starts
from .celery import app as celery_app

__all__ = ('celery_app',)
"""
========================================
CELERY CONFIGURATION FOR SHOPEASE
========================================

This file configures Celery for background task processing.

Architecture:
- Broker: Redis (message queue)
- Backend: Redis (result storage)
- Tasks: Order emails, OTP SMS, stock updates, analytics logging
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Create Celery app
app = Celery('shopease')

# Load config from Django settings with CELERY_ namespace
# This means all Celery config vars must start with CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed apps
# Looks for tasks.py in each app directory
app.autodiscover_tasks()

# Celery Beat Schedule (Periodic Tasks)
app.conf.beat_schedule = {
    # Clean expired sessions every day at 2 AM
    'clean-sessions-daily': {
        'task': 'apps.accounts.tasks.clean_expired_sessions',
        'schedule': crontab(hour=2, minute=0),
    },
    # Update product analytics every hour
    'update-product-analytics': {
        'task': 'apps.admin_panel.tasks.update_product_analytics',
        'schedule': crontab(minute=0),  # Every hour
    },
    # Send abandoned cart reminders every 6 hours
    'send-abandoned-cart-reminders': {
        'task': 'apps.cart.tasks.send_abandoned_cart_reminders',
        'schedule': crontab(minute=0, hour='*/6'),
    },
}

@app.task(bind=True)
def debug_task(self):
    """Test task to verify Celery is working."""
    print(f'Request: {self.request!r}')

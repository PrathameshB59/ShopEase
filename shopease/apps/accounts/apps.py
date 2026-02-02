"""
========================================
ACCOUNTS APP CONFIGURATION
========================================
Handles user authentication, registration, and profiles.
"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """
    Configuration for accounts application.
    
    Handles:
    - User registration
    - Login/logout
    - Password reset
    - User profiles
    - Account settings
    """
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    verbose_name = 'User Accounts'
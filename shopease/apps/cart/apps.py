"""
========================================
CART APP CONFIGURATION
========================================
Django app configuration for shopping cart.
"""

from django.apps import AppConfig


class CartConfig(AppConfig):
    """
    Configuration for the cart application.
    
    CRITICAL: The 'name' must match the path in INSTALLED_APPS
    - INSTALLED_APPS has: 'apps.cart'
    - So name must be: 'apps.cart'
    
    If these don't match, Django can't import the app.
    """
    
    # BigAutoField: Use 64-bit integers for primary keys
    # Supports 9,223,372,036,854,775,807 records (way more than needed)
    default_auto_field = 'django.db.models.BigAutoField'
    
    # MUST match the path in INSTALLED_APPS
    # INSTALLED_APPS = ['apps.cart'] → name = 'apps.cart'
    name = 'apps.cart'
    
    # Human-readable name (shows in admin)
    verbose_name = 'Shopping Cart'
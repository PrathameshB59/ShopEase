"""
========================================
CORE URLs - Homepage Routing
========================================
Maps URL paths to views for the core app.

Security:
- Uses Django's path() which sanitizes URLs automatically
- No user input in URL patterns (prevents injection)
"""

from django.urls import path
from . import views  # Import views from current package

# URL patterns for core app
# These handle the main site pages (homepage, about, contact, etc.)
urlpatterns = [
    # Smart landing page - Redirects based on authentication status and role
    # Anonymous users → Login page
    # Logged-in staff → Admin dashboard (port 8080)
    # Logged-in customers → Customer home page
    path('', views.landing_page, name='landing'),

    # Homepage - Shows featured products and categories
    # Actual home page for authenticated customers
    path('home/', views.home, name='home'),
]
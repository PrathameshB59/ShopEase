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
    # Homepage - Shows featured products and categories
    # path('') matches the root URL: http://example.com/
    # views.home is the view function that processes the request
    # name='home' allows reverse URL lookup in templates: {% url 'home' %}
    path('', views.home, name='home'),
]
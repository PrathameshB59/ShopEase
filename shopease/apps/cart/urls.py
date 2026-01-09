"""
========================================
CART URL CONFIGURATION
========================================
Routes for shopping cart operations.
"""

from django.urls import path
from . import views

# Namespace for cart URLs
# Access as: {% url 'cart:view' %}
app_name = 'cart'

urlpatterns = [
    # ==========================================
    # CART PAGE
    # ==========================================
    
    # View cart
    # GET: Display cart page with all items
    path('', views.cart_view, name='view'),
    
    # ==========================================
    # CART OPERATIONS (AJAX)
    # ==========================================
    
    # Add to cart
    # POST (AJAX): Add product to cart
    path('add/', views.add_to_cart, name='add'),
    
    # Update cart item
    # POST (AJAX): Update item quantity
    path('update/', views.update_cart, name='update'),
    
    # Remove from cart
    # POST (AJAX): Remove item from cart
    path('remove/', views.remove_from_cart, name='remove'),
    
    # Clear cart
    # POST (AJAX): Remove all items
    path('clear/', views.clear_cart, name='clear'),
    
    # Get cart data
    # GET (AJAX): Fetch current cart data
    path('data/', views.get_cart_data, name='data'),
]
"""
========================================
CART URLs - Routing Configuration
========================================
Maps URLs to cart view functions.

URL Pattern: /cart/...
"""

from django.urls import path
from . import views

app_name = 'cart'  # Namespace for cart URLs

urlpatterns = [
    # Cart view page
    # URL: /cart/
    # View: Display cart items
    path('', views.cart_view, name='cart_view'),
    
    # Add to cart (AJAX)
    # URL: /cart/add/
    # Method: POST
    # Body: {"product_id": 123, "quantity": 1}
    path('add/', views.add_to_cart, name='add_to_cart'),
    
    # Update cart item quantity (AJAX)
    # URL: /cart/update/5/
    # Method: POST
    # Body: {"quantity": 3}
    path('update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    
    # Remove item from cart (AJAX)
    # URL: /cart/remove/5/
    # Method: POST
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # Get cart data (AJAX)
    # URL: /cart/data/
    # Method: GET
    # Returns: JSON with cart stats
    path('data/', views.cart_data, name='cart_data'),
    
    # Clear cart
    # URL: /cart/clear/
    # Method: POST
    path('clear/', views.clear_cart, name='clear_cart'),
]
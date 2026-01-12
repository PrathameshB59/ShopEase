"""
========================================
CHECKOUT URLs - FAKE VERSION (Development)
========================================

Simplified URL patterns without payment callbacks.

Copy this to: apps/orders/urls.py
"""

from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Checkout page
    # URL: /checkout/
    # Shows checkout form and processes order
    path('checkout/', views.checkout, name='checkout'),
    
    # Order list (order history)
    # URL: /orders/
    # Shows all user's orders
    path('orders/', views.order_list, name='order_list'),
    
    # Order detail
    # URL: /orders/<uuid>/
    # Shows single order details
    path('orders/<uuid:order_id>/', views.order_detail, name='order_detail'),
    
    # Cancel order
    # URL: /orders/<uuid>/cancel/
    # Cancels an order (POST only)
    path('orders/<uuid:order_id>/cancel/', views.cancel_order, name='cancel_order'),
]
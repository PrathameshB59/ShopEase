# accounts/urls.py
"""
ACCOUNTS APP URL CONFIGURATION
================================
URLs for authentication and user management.
"""

from django.urls import path
from . import views, admin_views

app_name = 'accounts'

urlpatterns = [
    # ========== AUTHENTICATION ==========
    # Combined login/register page
    path('auth/', views.login_register_view, name='auth'),
    
    # Authentication handlers
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # User profile
    path('profile/', views.profile_view, name='profile'),
    
    # ========== ADMIN PANEL ==========
    # Dashboard
    path('admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    
    # Product Management
    path('admin/products/', admin_views.admin_products, name='admin_products'),
    
    # Order Management
    path('admin/orders/', admin_views.admin_orders, name='admin_orders'),
    path('admin/orders/<int:order_id>/', admin_views.admin_order_detail, name='admin_order_detail'),
    path('admin/orders/<int:order_id>/update-status/', admin_views.admin_update_order_status, name='admin_update_order_status'),
    
    # User Management
    path('admin/users/', admin_views.admin_users, name='admin_users'),
    
    # Category Management
    path('admin/categories/', admin_views.admin_categories, name='admin_categories'),
    
    # Analytics
    path('admin/analytics/', admin_views.admin_analytics, name='admin_analytics'),
    
    # Settings
    path('admin/settings/', admin_views.admin_settings, name='admin_settings'),
]
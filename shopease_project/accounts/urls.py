# accounts/urls.py
"""
ACCOUNTS APP URL CONFIGURATION
================================
URLs for authentication and user management.
"""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Combined login/register page
    path('auth/', views.login_register_view, name='auth'),
    
    # Authentication handlers
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # User profile
    path('profile/', views.profile_view, name='profile'),
]
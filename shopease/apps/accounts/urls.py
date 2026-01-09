"""
========================================
ACCOUNTS URL CONFIGURATION
========================================
Routes for authentication and user management.
"""

from django.urls import path
from . import views

# Namespace for accounts URLs
# Access as: {% url 'accounts:login' %}
app_name = 'accounts'

urlpatterns = [
    # ==========================================
    # AUTHENTICATION
    # ==========================================
    
    # Registration
    # GET: Display registration form
    # POST: Process registration
    path('register/', views.register, name='register'),
    
    # Login
    # GET: Display login form
    # POST: Process login
    path('login/', views.user_login, name='login'),
    
    # Logout
    # POST: Log user out (CSRF protected)
    path('logout/', views.user_logout, name='logout'),
    
    # ==========================================
    # PROFILE MANAGEMENT
    # ==========================================
    
    # User profile (view and edit)
    # GET: Display profile
    # POST: Update profile
    path('profile/', views.profile, name='profile'),
    
    # Dashboard (TODO: implement)
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # ==========================================
    # PASSWORD RESET
    # ==========================================
    
    # Step 1: Request password reset
    # User enters email
    path(
        'password-reset/',
        views.CustomPasswordResetView.as_view(),
        name='password_reset'
    ),
    
    # Step 2: Email sent confirmation
    path(
        'password-reset/done/',
        views.CustomPasswordResetDoneView.as_view(),
        name='password_reset_done'
    ),
    
    # Step 3: Set new password
    # Token in URL validates request
    path(
        'reset/<uidb64>/<token>/',
        views.CustomPasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
    ),
    
    # Step 4: Success message
    path(
        'reset/done/',
        views.CustomPasswordResetCompleteView.as_view(),
        name='password_reset_complete'
    ),

    # ==========================================
    # COMBINED AUTH PAGE (NEW)
    # ==========================================
    path('auth/', views.auth_page, name='auth'),
    
    # ==========================================
    # OTP AUTHENTICATION (NEW)
    # ==========================================
    path('send-otp/', views.send_otp, name='send_otp'),
    path('verify-otp/', views.verify_otp_login, name='verify_otp'),
    
    # ==========================================
    # ORIGINAL AUTHENTICATION (Keep for backward compatibility)
    # ==========================================
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
]
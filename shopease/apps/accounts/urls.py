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

    # Token-based auto-login for cross-port authentication
    # GET: Validate token and auto-login to admin server
    # Used when admin users log in on port 8000 and are redirected to port 8080
    path('admin-auto-login/', views.admin_auto_login, name='admin_auto_login'),

    # ==========================================
    # PROFILE MANAGEMENT
    # ==========================================
    
    # User profile (view and edit)
    # GET: Display profile
    # POST: Update profile
    path('profile/', views.profile, name='profile'),

    # Session termination
    # POST: Terminate a specific session
    path('sessions/<int:session_id>/terminate/', views.terminate_session, name='terminate_session'),

    # Dashboard (TODO: implement)
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # ==========================================
    # PASSWORD RESET (For users who forgot password)
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
    # PASSWORD CHANGE (For logged-in users)
    # ==========================================

    # Change password (requires current password)
    path(
        'password-change/',
        views.CustomPasswordChangeView.as_view(),
        name='password_change'
    ),

    # Password change success
    path(
        'password-change/done/',
        views.CustomPasswordChangeDoneView.as_view(),
        name='password_change_done'
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
]
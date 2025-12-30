# accounts/views.py
"""
AUTHENTICATION VIEWS
=====================
Handles user login, registration, and logout functionality.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import User


def login_register_view(request):
    """
    COMBINED LOGIN/REGISTER VIEW
    =============================
    Shows sliding login/register page.
    Handles both login and registration in one view.
    
    URL: /accounts/auth/
    Template: accounts/auth.html
    """
    # If user is already logged in, redirect to home
    if request.user.is_authenticated:
        return redirect('home')
    
    return render(request, 'accounts/auth.html')


@require_http_methods(["POST"])
def register_view(request):
    """
    REGISTRATION HANDLER
    ====================
    Processes user registration form submission.
    
    Form fields:
    - username
    - email
    - password1
    - password2
    """
    # Get form data
    username = request.POST.get('username')
    email = request.POST.get('email')
    password1 = request.POST.get('password1')
    password2 = request.POST.get('password2')
    
    # Validation
    if not all([username, email, password1, password2]):
        messages.error(request, 'All fields are required!')
        return redirect('accounts:auth')
    
    if password1 != password2:
        messages.error(request, 'Passwords do not match!')
        return redirect('accounts:auth')
    
    if len(password1) < 6:
        messages.error(request, 'Password must be at least 6 characters!')
        return redirect('accounts:auth')
    
    # Check if username already exists
    if User.objects.filter(username=username).exists():
        messages.error(request, 'Username already taken!')
        return redirect('accounts:auth')
    
    # Check if email already exists
    if User.objects.filter(email=email).exists():
        messages.error(request, 'Email already registered!')
        return redirect('accounts:auth')
    
    try:
        # Create new user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            role='CUSTOMER'  # Default role
        )
        
        # Log the user in
        login(request, user)
        
        messages.success(request, f'Welcome {username}! Your account has been created successfully.')
        return redirect('home')
        
    except Exception as e:
        messages.error(request, f'Registration failed: {str(e)}')
        return redirect('accounts:auth')


@require_http_methods(["POST"])
def login_view(request):
    """
    LOGIN HANDLER
    =============
    Processes user login form submission.
    
    Form fields:
    - username
    - password
    """
    # Get form data
    username = request.POST.get('username')
    password = request.POST.get('password')
    
    # Validation
    if not username or not password:
        messages.error(request, 'Username and password are required!')
        return redirect('accounts:auth')
    
    # Authenticate user
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        # Login successful
        login(request, user)
        messages.success(request, f'Welcome back, {user.username}!')
        
        # Redirect to next page or home
        next_page = request.GET.get('next', 'home')
        return redirect(next_page)
    else:
        # Login failed
        messages.error(request, 'Invalid username or password!')
        return redirect('accounts:auth')


@login_required
def logout_view(request):
    """
    LOGOUT HANDLER
    ==============
    Logs out the current user.
    
    URL: /accounts/logout/
    """
    username = request.user.username
    logout(request)
    messages.success(request, f'Goodbye, {username}! You have been logged out.')
    return redirect('home')


@login_required
def profile_view(request):
    """
    USER PROFILE VIEW
    =================
    Shows user profile page.
    
    URL: /accounts/profile/
    Template: accounts/profile.html
    """
    return render(request, 'accounts/profile.html', {
        'user': request.user
    })
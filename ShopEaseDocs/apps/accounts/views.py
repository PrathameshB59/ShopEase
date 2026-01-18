"""
Authentication views for ShopEase Documentation.

Uses ShopEase MySQL database for user authentication.
Supports login with either username OR email.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect


@csrf_protect
@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    Handle user login using ShopEase database credentials.

    Supports login with either username OR email (via EmailOrUsernameBackend).

    Redirects based on user role:
    - Superusers -> Code Documentation
    - Regular users -> Help Center
    """
    # Redirect if already logged in
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('code_docs:overview')
        return redirect('help_center:index')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        # Validate input
        if not username or not password:
            messages.error(request, 'Please enter both username/email and password.')
            return render(request, 'accounts/login.html')

        # Authenticate user (EmailOrUsernameBackend handles email/username)
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Check if account is active
            if not user.is_active:
                messages.error(
                    request,
                    'Your account has been deactivated. Please contact support.'
                )
                return render(request, 'accounts/login.html')

            # Login successful
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')

            # Redirect based on role
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)

            if request.user.is_superuser:
                return redirect('code_docs:overview')
            return redirect('help_center:index')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')


@require_http_methods(["GET", "POST"])
def logout_view(request):
    """Handle user logout."""
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
    return redirect('core:home')


def access_denied(request):
    """Display access denied page for unauthorized access attempts."""
    return render(request, 'accounts/access_denied.html')

"""
Authentication decorators for ShopEase Documentation.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def superadmin_required(view_func):
    """
    Decorator that requires the user to be a superuser (is_superuser=True).

    If the user is not authenticated, redirects to login.
    If the user is not a superuser, redirects to help center with an error message.

    Usage:
        @superadmin_required
        def my_view(request):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Please login to access this page.')
            return redirect('accounts:login')

        if not request.user.is_superuser:
            messages.error(request, 'Access denied. Super Admin privileges required.')
            return redirect('help_center:index')

        return view_func(request, *args, **kwargs)

    return wrapper


def login_required_custom(view_func):
    """
    Custom login required decorator with proper redirect and message.

    Usage:
        @login_required_custom
        def my_view(request):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Please login to access this page.')
            return redirect('accounts:login')

        return view_func(request, *args, **kwargs)

    return wrapper
